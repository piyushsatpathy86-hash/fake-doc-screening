"""
modules/risk.py
Combines validation errors, tamper score, face match, and liveness
into a single overall risk score.

Weights:
  validation -> up to 45 points (15 per error)
  tamper     -> up to 30 points (tamper_score * 30)
  face match -> 30 points if no match
  liveness   -> 10 points if failed

Genuine Check:
  If face_match is True and tamper_score < 0.15, validation errors
  are ignored (set to 0) because OCR may miss fields on synthetic
  documents but the document is likely authentic.
"""


def calculate_risk(validation_errors: list, tamper_score: float, face_match: bool, liveness_passed: bool):
    """
    Parameters
    ----------
    validation_errors : list of error strings
    tamper_score : float, expected range 0-1 (from modules/tamper.py)
    face_match : bool, whether the live photo matches the document photo
    liveness_passed : bool, whether the liveness check passed

    Returns
    -------
    dict with keys: risk_score (0-100), risk_level ("LOW"/"MEDIUM"/"HIGH"), breakdown
    """

    # ---- 1. Validation score (max 45) ----
    num_errors = len(validation_errors) if validation_errors else 0
    tamper_score = max(0.0, min(float(tamper_score), 1.0))

    # Genuine check: if face matches and tamper is low, ignore validation errors
    if face_match and tamper_score < 0.15:
        validation_component = 0
    else:
        validation_component = min(num_errors * 15, 45)

    # ---- 2. Tamper score (max 30) ----
    tamper_component = tamper_score * 30

    # ---- 3. Face match (30) ----
    face_component = 0 if face_match else 30

    # ---- 4. Liveness (10) ----
    liveness_component = 0 if liveness_passed else 10

    total_score = validation_component + tamper_component + face_component + liveness_component
    total_score = round(min(total_score, 100), 2)

    # Adjusted thresholds
    if total_score >= 60:
        risk_level = "HIGH"
    elif total_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": total_score,
        "risk_level": risk_level,
        "breakdown": {
            "validation_component": round(validation_component, 2),
            "tamper_component": round(tamper_component, 2),
            "face_component": round(face_component, 2),
            "liveness_component": round(liveness_component, 2),
        },
    }


if __name__ == "__main__":
    # Test 1: Face match true, low tamper -> LOW (validation ignored)
    result1 = calculate_risk(
        validation_errors=["Expiry date could not be extracted", "MRZ checksum validation failed"],
        tamper_score=0.0255,
        face_match=True,
        liveness_passed=True,
    )
    print("Genuine case (should be LOW):", result1)

    # Test 2: Face mismatch -> HIGH
    result2 = calculate_risk(
        validation_errors=["Expiry date could not be extracted", "MRZ checksum validation failed"],
        tamper_score=0.0255,
        face_match=False,
        liveness_passed=True,
    )
    print("Mismatch case (should be HIGH):", result2)
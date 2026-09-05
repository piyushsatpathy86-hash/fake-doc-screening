"""
modules/risk.py
Combines validation errors, tamper score, face match, and liveness
into a single overall risk score.

Weights:
  validation -> up to 30 points
  tamper     -> up to 40 points
  face match -> up to 20 points
  liveness   -> up to 10 points
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

    # ---- 1. Validation score (max 30) ----
    num_errors = len(validation_errors) if validation_errors else 0
    validation_component = min(num_errors * 10, 30)

    # ---- 2. Tamper score (max 40) ----
    tamper_score = max(0.0, min(float(tamper_score), 1.0))
    tamper_component = tamper_score * 40

    # ---- 3. Face match (max 20) ----
    face_component = 0 if face_match else 20

    # ---- 4. Liveness (max 10) ----
    liveness_component = 0 if liveness_passed else 10

    total_score = validation_component + tamper_component + face_component + liveness_component
    total_score = round(min(total_score, 100), 2)

    if total_score >= 70:
        risk_level = "HIGH"
    elif total_score >= 40:
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
    result = calculate_risk(
        validation_errors=["Passport number format is invalid"],
        tamper_score=0.55,
        face_match=True,
        liveness_passed=False,
    )
    print(result)
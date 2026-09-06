"""
modules/risk.py
Weighted risk scoring, combining all screening signals into a
single 0-100 score and LOW/MEDIUM/HIGH verdict.

Weights (out of 100):
  validation_component : up to 20  (missing/invalid fields, expiry, blacklist, MRZ)
  tamper_component      : up to 40  (ELA-based tamper score, see tamper.py)
  noise_component       : up to 10  (sensor-noise inconsistency, see noise_analysis.py)
  face_component        : 50 flat if no face match, else 0
  liveness_component    : 10 flat if liveness fails, else 0
"""


def calculate_risk(validation_errors, tamper_score, noise_score, face_match, liveness_passed):
    num_errors = len(validation_errors) if validation_errors else 0

    tamper_score = max(0.0, min(float(tamper_score or 0.0), 1.0))
    noise_score = max(0.0, min(float(noise_score or 0.0), 1.0))

    validation_component = min(num_errors * 10, 20)
    tamper_component = tamper_score * 40
    noise_component = noise_score * 10
    face_component = 0 if face_match else 50   # was 30
    liveness_component = 0 if liveness_passed else 10

    total_score = (
        validation_component
        + tamper_component
        + noise_component
        + face_component
        + liveness_component
    )
    total_score = round(min(total_score, 100), 2)

    if total_score >= 50:          # was 60
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
            "noise_component": round(noise_component, 2),
            "face_component": round(face_component, 2),
            "liveness_component": round(liveness_component, 2),
        },
    }


if __name__ == "__main__":
    print(calculate_risk(
        validation_errors=["Expiry date could not be extracted"],
        tamper_score=0.05,
        noise_score=0.12,
        face_match=True,
        liveness_passed=True,
    ))
    print(calculate_risk(
        validation_errors=["MRZ checksum validation failed", "Document has expired"],
        tamper_score=0.9,
        noise_score=0.6,
        face_match=False,
        liveness_passed=True,
    ))
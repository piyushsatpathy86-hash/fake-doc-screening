def calculate_risk(validation_errors, tamper_score, face_match):
    risk = 0
    
    # Validation penalty (max 30)
    risk += min(len(validation_errors) * 10, 30)
    
    # Tampering penalty (max 40)
    risk += tamper_score * 40
    
    # Face penalty (max 30)
    if not face_match:
        risk += 30
    
    risk = min(risk, 100)
    
    if risk < 30:
        level = "LOW"
    elif risk < 60:
        level = "MEDIUM"
    else:
        level = "HIGH"
    
    return risk, level
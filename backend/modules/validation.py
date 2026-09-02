def validate_document(fields):
    errors = []
    if not fields:
        errors.append("No fields extracted")
    return errors
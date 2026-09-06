"""
modules/validation.py
Validates fields extracted by ocr.py based on the detected document type.
"""

import os
import re
import csv
from datetime import datetime

BLACKLIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "blacklist.csv",
)


def _load_blacklist() -> set:
    """Read passport numbers from data/blacklist.csv into a set."""
    blacklist = set()
    if not os.path.exists(BLACKLIST_PATH):
        return blacklist

    try:
        with open(BLACKLIST_PATH, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            # Skip header row if present
            start_index = 1 if rows and rows[0][0].lower() == "passport_number" else 0
            for row in rows[start_index:]:
                if row:
                    blacklist.add(row[0].strip().upper())
    except Exception:
        pass

    return blacklist


def _try_parse_date(date_str: str):
    """Try a few common date formats seen in MRZ / OCR output."""
    for fmt in ("%Y-%m-%d", "%y%m%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue
    return None


def validate_document(fields: dict, document_type: str = None) -> list:
    """
    Run validation checks based on the document type.
    Returns a list of error strings (empty list = document looks valid).
    """
    errors = []

    if not fields:
        return ["No fields extracted from document"]

    doc_type = (document_type or "").lower()

    # 1. Passport-specific checks (applied if passport, unknown, or empty)
    if doc_type in ("passport", "unknown", ""):
        passport_number = fields.get("passport_number")

        if not passport_number:
            errors.append("Passport number could not be extracted")
        elif not re.match(r"^[A-Za-z][0-9]{7}$", str(passport_number).strip()):
            errors.append("Passport number format is invalid (expected: 1 letter + 7 digits)")

        expiry_date = fields.get("date_of_expiry")
        if expiry_date:
            parsed_expiry = _try_parse_date(expiry_date)
            if parsed_expiry is None:
                errors.append("Expiry date format is invalid")
            elif parsed_expiry < datetime.now():
                errors.append("Document has expired")
        else:
            errors.append("Expiry date could not be extracted")

        # Blacklist check
        if passport_number:
            blacklist = _load_blacklist()
            if str(passport_number).strip().upper() in blacklist:
                errors.append(f"Passport number {passport_number} appears on the blacklist")

        # MRZ checksum validity.
        # raw_mrz_valid has three states now (see ocr.py):
        #   False -> an MRZ WAS read but its checksum failed -> real red flag
        #   None  -> no MRZ could be read at all (fell back to OCR) ->
        #            informational only, NOT a forgery signal by itself
        #   True  -> checksum passed, no error
        mrz_status = fields.get("raw_mrz_valid")
        if mrz_status is False and passport_number:
            errors.append("MRZ checksum validation failed")
        elif mrz_status is None and passport_number:
            errors.append("MRZ could not be read (OCR fallback used)")

    # 2. Aadhaar-specific checks
    elif doc_type == "aadhaar":
        aadhaar_number = fields.get("aadhaar_number") or fields.get("passport_number")
        if not aadhaar_number:
            errors.append("Aadhaar number could not be extracted")
        elif not re.match(r"^\d{12}$", str(aadhaar_number).replace(" ", "")):
            errors.append("Aadhaar number format is invalid (expected: 12 digits)")

    # 3. Driving license-specific checks
    elif doc_type == "driving_license":
        dl_number = fields.get("dl_number") or fields.get("passport_number")
        if not dl_number:
            errors.append("Driving license number could not be extracted")
        # Basic DL format: two letters, two digits, space, 11 alphanumeric (example)
        elif not re.match(r"^[A-Z]{2}\d{2}\s?[A-Z0-9]{11}$", str(dl_number).strip()):
            errors.append("Driving license number format is invalid")

    # 4. Visa-specific checks
    elif doc_type == "visa":
        visa_number = fields.get("visa_number") or fields.get("passport_number")
        if not visa_number:
            errors.append("Visa number could not be extracted")
        elif not re.match(r"^[A-Za-z]\d{7}$", str(visa_number).strip()):
            errors.append("Visa number format is invalid (expected: letter + 7 digits)")

    return errors


if __name__ == "__main__":
    sample_passport = {
        "passport_number": "A1234567",
        "date_of_expiry": "2030-01-01",
        "raw_mrz_valid": True,
    }
    sample_passport_fallback = {
        "passport_number": "A1234567",
        "date_of_expiry": "2030-01-01",
        "raw_mrz_valid": None,
    }
    sample_aadhaar = {
        "aadhaar_number": "951234678901",
    }
    print("Passport (MRZ read OK):", validate_document(sample_passport, "passport"))
    print("Passport (OCR fallback):", validate_document(sample_passport_fallback, "passport"))
    print("Aadhaar:", validate_document(sample_aadhaar, "aadhaar"))
"""
modules/validation.py
Validates fields extracted by ocr.py:
  - expiry date must not be in the past
  - passport number must match "letter + 7 digits" format
  - passport number must not appear in data/blacklist.csv
Returns a list of human-readable error strings.
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


def validate_document(fields: dict) -> list:
    """
    Run validation checks on extracted fields.
    Returns a list of error strings (empty list = document looks valid).
    """
    errors = []

    if not fields:
        return ["No fields extracted from document"]

    passport_number = fields.get("passport_number")

    # 1. Passport number format: 1 letter followed by 7 digits (e.g. A1234567)
    if not passport_number:
        errors.append("Passport number could not be extracted")
    elif not re.match(r"^[A-Za-z][0-9]{7}$", str(passport_number).strip()):
        errors.append("Passport number format is invalid (expected: 1 letter + 7 digits)")

    # 2. Expiry date must not be in the past
    expiry_date = fields.get("date_of_expiry")
    if expiry_date:
        parsed_expiry = _try_parse_date(expiry_date)
        if parsed_expiry is None:
            errors.append("Expiry date format is invalid")
        elif parsed_expiry < datetime.now():
            errors.append("Document has expired")
    else:
        errors.append("Expiry date could not be extracted")

    # 3. Blacklist check
    if passport_number:
        blacklist = _load_blacklist()
        if str(passport_number).strip().upper() in blacklist:
            errors.append(f"Passport number {passport_number} appears on the blacklist")

    # 4. MRZ checksum validity, if OCR reported it
    if fields.get("raw_mrz_valid") is False and fields.get("passport_number"):
        errors.append("MRZ checksum validation failed")

    return errors


if __name__ == "__main__":
    sample_fields = {
        "passport_number": "A1234567",
        "date_of_expiry": "2030-01-01",
        "raw_mrz_valid": True,
    }
    print(validate_document(sample_fields))
"""Basic validation for fields read from a passport MRZ."""

import csv
import re
from datetime import datetime, date
from pathlib import Path


BLACKLIST_FILE = Path(__file__).resolve().parents[2] / "data" / "blacklist.csv"


def _parse_date(value):
    """Accept common MRZ (YYMMDD) and ISO (YYYY-MM-DD) date formats."""
    value = str(value or "")
    for pattern in ("%y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    return None


def _blacklisted_numbers():
    with BLACKLIST_FILE.open(newline="", encoding="utf-8") as file:
        return {row["passport_number"].strip() for row in csv.DictReader(file)}


def validate_document(fields):
    """Return a list of simple passport validation errors."""
    errors = []
    passport_number = str(fields.get("passport_number", "")).strip()
    expiry = _parse_date(fields.get("date_of_expiry"))

    if not expiry:
        errors.append("Invalid expiry date format")
    elif expiry < date.today():
        errors.append("Passport has expired")

    if not re.fullmatch(r"[A-Z]\d{7}", passport_number):
        errors.append("Invalid passport number format")
    elif passport_number in _blacklisted_numbers():
        errors.append("Passport number is blacklisted")

    return errors

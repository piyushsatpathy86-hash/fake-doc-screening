"""
modules/ocr.py
Extracts identity fields from a document image.
Name extraction: ONLY from explicit labels (Surname / Given Name / Name:).
"""

import os
import re

try:
    from passporteye import read_mrz
except ImportError:
    read_mrz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


def _empty_fields():
    return {
        "name": None,
        "passport_number": None,
        "nationality": None,
        "date_of_birth": None,
        "date_of_expiry": None,
        "gender": None,
        "raw_mrz_valid": None,
        "aadhaar_number": None,
        "dl_number": None,
        "visa_number": None,
    }


def _extract_with_mrz(image_path: str) -> dict:
    fields = _empty_fields()
    if read_mrz is None:
        return None
    try:
        mrz = read_mrz(image_path)
        if mrz is None:
            return None
        data = mrz.to_dict()
        fields["name"] = f"{data.get('names', '')} {data.get('surname', '')}".strip()
        fields["passport_number"] = data.get("number")
        fields["nationality"] = data.get("nationality")
        fields["date_of_birth"] = data.get("date_of_birth")
        fields["date_of_expiry"] = data.get("expiration_date")
        fields["gender"] = data.get("sex")
        fields["raw_mrz_valid"] = data.get("valid_score", 0) >= 80
        return fields
    except Exception:
        return None


def _extract_with_ocr_fallback(image_path: str) -> dict:
    fields = _empty_fields()
    if pytesseract is None or Image is None:
        fields["error"] = "pytesseract/PIL not installed"
        return fields
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        text_upper = text.upper()

        # Passport number: letter + 7 digits (e.g., T1234567)
        pm = re.search(r"\b([A-Z][0-9]{7})\b", text_upper)
        if pm:
            fields["passport_number"] = pm.group(1)

        # Aadhaar number (12 digits, possibly spaced)
        am = re.search(r"\b(\d{4}\s?\d{4}\s?\d{4})\b", text)
        if am:
            fields["aadhaar_number"] = am.group(1).replace(" ", "")

        # DL number (e.g., MH01 20260000001)
        dl = re.search(r"\b([A-Z]{2}\d{2}\s?[A-Z0-9]{11})\b", text_upper)
        if dl:
            fields["dl_number"] = dl.group(1)

        # Visa number (letter + 7 digits)
        vm = re.search(r"\b([A-Z]\d{7})\b", text_upper)
        if vm:
            fields["visa_number"] = vm.group(1)

        # ---------- NAME EXTRACTION (STRICT: only explicit labels) ----------
        # We look for "Surname" and "Given Name(s)" labels separately.
        # After the label, we take the next non-empty line that contains
        # only alphabetic characters and spaces (no digits, no punctuation).
        def get_label_value(label_pattern):
            m = re.search(label_pattern, text, re.IGNORECASE)
            if not m:
                return None
            # Find the start of the value after the label
            start = m.end()
            # Get remaining text
            remaining = text[start:]
            # Take first non-empty line
            for line in remaining.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Only accept if line has only letters and spaces
                if re.fullmatch(r"[A-Za-z\s.]+", line):
                    return line
                return None  # if next line isn't clean, don't guess
            return None

        surname = get_label_value(r"Surname\s*[:/\n]+")
        given = get_label_value(r"Given Name(?:\(s\))?\s*[:/\n]+")

        if surname or given:
            name = f"{given or ''} {surname or ''}".strip()
            fields["name"] = name or None
        else:
            # Only "Name:" label (not "Passport No" or anything else)
            name_match = re.search(r"\bName\s*[:]\s*([A-Za-z]+(?:\s[A-Za-z]+)*)", text, re.IGNORECASE)
            if name_match:
                fields["name"] = name_match.group(1).strip()
            else:
                fields["name"] = None

        # ---------- DATE OF BIRTH ----------
        dob_labeled = re.search(
            r"(?:DOB|Date of Birth|\u091c\u0928\u094d\u092e\s*\u0924\u093f\u0925\u093f)[:\s/]*(\d{2}[/-]\d{2}[/-]\d{4})",
            text, re.IGNORECASE,
        )
        if dob_labeled:
            fields["date_of_birth"] = dob_labeled.group(1)
        else:
            dob = re.search(r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b", text)
            if dob:
                fields["date_of_birth"] = dob.group(1)

        # ---------- EXPIRY DATE ----------
        expiry_match = re.search(
            r"(?:Date of Expiry|EXPIRY|EXP|Valid Till|Valid Upto|Valid Until|"
            r"Visa Expiry|Visa Valid Until|Visa Valid Upto)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})",
            text, re.IGNORECASE,
        )
        if expiry_match:
            fields["date_of_expiry"] = expiry_match.group(1)

        # ---------- GENDER ----------
        gender_full = re.search(r"\b(Male|Female)\b", text, re.IGNORECASE)
        if gender_full:
            fields["gender"] = gender_full.group(1)[0].upper()
        else:
            gender_abbr = re.search(r"(?:Sex|Gender)[:\s]*([MF])", text, re.IGNORECASE)
            if not gender_abbr:
                gender_abbr = re.search(r"\b(M|F)\b", text_upper)
            if gender_abbr:
                fields["gender"] = gender_abbr.group(1).upper()

        fields["raw_mrz_valid"] = None
        fields["ocr_raw_text"] = text[:500]
    except Exception as e:
        fields["error"] = f"OCR fallback failed: {str(e)}"
    return fields


def extract_fields(image_path: str) -> dict:
    if not os.path.exists(image_path):
        fields = _empty_fields()
        fields["error"] = "Image file not found"
        return fields

    mrz_fields = _extract_with_mrz(image_path)
    if mrz_fields and mrz_fields.get("passport_number"):
        return mrz_fields

    return _extract_with_ocr_fallback(image_path)


if __name__ == "__main__":
    import json
    print(json.dumps(extract_fields("sample_passport.jpg"), indent=2))
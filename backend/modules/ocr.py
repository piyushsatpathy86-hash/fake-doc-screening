"""
modules/ocr.py
Extracts identity fields from a document image.

`raw_mrz_valid` now has THREE possible states, not two:
  True  -> PassportEye read the MRZ and its checksum validated
  False -> PassportEye read an MRZ but the checksum FAILED
           (a real forgery/corruption signal)
  None  -> No MRZ could be read at all, so we fell back to plain
           OCR (very common on photos/scans of non-MRZ documents
           like Aadhaar/DL, or low-quality passport photos) --
           this is NOT the same thing as a failed checksum and
           should not be scored as one.
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
        passport_match = re.search(r"\b([A-Z][0-9]{7})\b", text_upper)
        if passport_match:
            fields["passport_number"] = passport_match.group(1)

        # ========== IMPROVED NAME EXTRACTION ==========
        # Try explicit passport labels first (Surname / Given Name(s))
        surname_match = re.search(r"Surname\s*[:/\n]+\s*([A-Z]+)", text, re.IGNORECASE)
        given_match = re.search(r"Given Name(?:\(s\))?\s*[:/\n]+\s*([A-Z\s.]+?)(?=\n|$)", text, re.IGNORECASE)

        surname = surname_match.group(1).strip() if surname_match else ""
        given = given_match.group(1).strip() if given_match else ""

        if surname or given:
            fields["name"] = f"{given} {surname}".strip()
        else:
            # Generic "Name:" label fallback
            name_match = re.search(r"(?:Name|Surname)[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text, re.IGNORECASE)
            if name_match:
                fields["name"] = name_match.group(1).strip()

        # Aadhaar/other card fallback: first suitable Title-Case line
        if not fields["name"]:
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for line in lines:
                # Line should look like a name: 2-3 words, each starting uppercase, only letters
                words = line.split()
                if 2 <= len(words) <= 3 and all(w.isalpha() and w[0].isupper() for w in words):
                    low_line = line.lower()
                    # Skip known non-name phrases
                    skip_phrases = [
                        "government of", "unique identification", "gender male",
                        "gender female", "date of", "valid till", "valid upto",
                        "aadhaar", "aadhar", "passport", "republic of india",
                        "issued", "dob", "date of birth"
                    ]
                    if not any(ph in low_line for ph in skip_phrases):
                        fields["name"] = line
                        break

        # Last resort: Title-Case two-word pattern
        if not fields["name"]:
            for candidate in re.finditer(r"\b([A-Z][a-z]+)\s([A-Z][a-z]+)\b", text):
                phrase = f"{candidate.group(1)} {candidate.group(2)}".lower()
                if phrase not in {
                    "government of", "unique identification", "gender male",
                    "gender female", "date of", "valid till", "valid upto",
                }:
                    fields["name"] = f"{candidate.group(1)} {candidate.group(2)}"
                    break
        # ================================================

        # Date of birth
        dob_labeled_match = re.search(
            r"(?:DOB|Date of Birth|\u091c\u0928\u094d\u092e\s*\u0924\u093f\u0925\u093f)[:\s/]*"
            r"(\d{2}[/-]\d{2}[/-]\d{4})",
            text,
            re.IGNORECASE,
        )
        if dob_labeled_match:
            fields["date_of_birth"] = dob_labeled_match.group(1)
        else:
            dob_match = re.search(r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b", text)
            if dob_match:
                fields["date_of_birth"] = dob_match.group(1)

        # Expiry date
        expiry_match = re.search(
            r"(?:Date of Expiry|EXPIRY|EXP|Valid Till|Valid Upto|Valid Until|"
            r"Visa Expiry|Visa Valid Until|Visa Valid Upto)[:\s]*"
            r"(\d{2}[/-]\d{2}[/-]\d{4})",
            text,
            re.IGNORECASE,
        )
        if expiry_match:
            fields["date_of_expiry"] = expiry_match.group(1)

        # Gender/Sex
        gender_match = re.search(r"(?:Sex|Gender)[:\s]*([MF])", text, re.IGNORECASE)
        if not gender_match:
            gender_match = re.search(r"\b(M|F)\b", text_upper)
        if gender_match:
            fields["gender"] = gender_match.group(1).upper()

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
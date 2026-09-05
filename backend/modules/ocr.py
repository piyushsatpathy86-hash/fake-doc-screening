"""
modules/ocr.py
Extracts identity fields from a document image.
Primary method: PassportEye MRZ reader (works for passports/visas
with a Machine Readable Zone).
Fallback: pytesseract raw text + regex, for documents without an MRZ
(e.g. Aadhaar, driving licence).
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
        "raw_mrz_valid": False,
    }


def _extract_with_mrz(image_path: str) -> dict:
    """Try reading the MRZ (Machine Readable Zone) of the document."""
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
    """Basic pytesseract text extraction + regex, used when MRZ reading fails."""
    fields = _empty_fields()

    if pytesseract is None or Image is None:
        fields["error"] = "pytesseract/PIL not installed"
        return fields

    try:
        text = pytesseract.image_to_string(Image.open(image_path))

        # Very simple regex heuristics - adjust to your document formats
        passport_match = re.search(r"\b([A-Z][0-9]{7})\b", text)
        if passport_match:
            fields["passport_number"] = passport_match.group(1)

        dob_match = re.search(r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b", text)
        if dob_match:
            fields["date_of_birth"] = dob_match.group(1)

        name_match = re.search(r"Name[:\s]+([A-Za-z ]+)", text)
        if name_match:
            fields["name"] = name_match.group(1).strip()

        fields["raw_mrz_valid"] = False
        fields["ocr_raw_text"] = text[:500]  # keep a short snippet for debugging
    except Exception as e:
        fields["error"] = f"OCR fallback failed: {str(e)}"

    return fields


def extract_fields(image_path: str) -> dict:
    """
    Main entry point used by main.py.
    Tries MRZ first (best for passports/visas), then falls back to
    generic OCR + regex for other document types.
    """
    if not os.path.exists(image_path):
        fields = _empty_fields()
        fields["error"] = "Image file not found"
        return fields

    mrz_fields = _extract_with_mrz(image_path)
    if mrz_fields and mrz_fields.get("passport_number"):
        return mrz_fields

    return _extract_with_ocr_fallback(image_path)


if __name__ == "__main__":
    print(extract_fields("sample_passport.jpg"))
"""
modules/document_type.py
Detects the type of identity document from an image using simple
heuristics: aspect ratio / dimensions plus keyword spotting in any
OCR'd text. This is a lightweight prototype-level classifier -
for production, train a proper image classifier (e.g. CNN).
"""

import os
import cv2

try:
    import pytesseract
except ImportError:
    pytesseract = None


# Passports/visas: MRZ booklets, roughly 125mm x 88mm -> ratio ~1.42
# Aadhaar/driving licence: credit-card sized, roughly 85.6mm x 54mm -> ratio ~1.58
PASSPORT_RATIO_RANGE = (1.30, 1.55)
CARD_RATIO_RANGE = (1.55, 1.75)

KEYWORDS = {
    "passport": ["passport", "republic of india", "type p"],
    "visa": ["visa", "entries", "duration of stay"],
    "aadhaar": ["aadhaar", "unique identification", "uidai"],
    "driving_license": ["driving licence", "driving license", "transport authority", "dl no"],
}


def _get_text(image_path: str) -> str:
    """Best-effort OCR text extraction used only for keyword spotting."""
    if pytesseract is None:
        return ""
    try:
        return pytesseract.image_to_string(cv2.imread(image_path)).lower()
    except Exception:
        return ""


def detect_document_type(image_path: str) -> str:
    """
    Return one of: "passport", "visa", "aadhaar", "driving_license", "unknown"
    """
    if not os.path.exists(image_path):
        return "unknown"

    image = cv2.imread(image_path)
    if image is None:
        return "unknown"

    height, width = image.shape[:2]
    ratio = max(width, height) / min(width, height) if min(width, height) > 0 else 0

    text = _get_text(image_path)

    # 1. Keyword-based detection (most reliable when OCR text is available)
    for doc_type, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return doc_type

    # 2. Fallback to aspect-ratio heuristic
    if PASSPORT_RATIO_RANGE[0] <= ratio <= PASSPORT_RATIO_RANGE[1]:
        return "passport"
    if CARD_RATIO_RANGE[0] <= ratio <= CARD_RATIO_RANGE[1]:
        return "aadhaar"  # could also be a driving licence; ambiguous by shape alone

    return "unknown"


if __name__ == "__main__":
    print(detect_document_type("sample_passport.jpg"))
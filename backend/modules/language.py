"""
modules/language.py
English/Hindi translation dictionary for the frontend and API messages.
"""

translations = {
    "en": {
        "title": "AI Document Screening System",
        "upload_doc": "Upload Document",
        "upload_live": "Upload / Capture Live Photo",
        "analyze": "Analyze",
        "risk_score": "Risk Score",
        "face_match": "Face Match",
        "tamper_score": "Tamper Score",
        "document_type": "Document Type",
        "validation_errors": "Validation Errors",
        "risk_low": "Low Risk",
        "risk_medium": "Medium Risk",
        "risk_high": "High Risk",
        "liveness_passed": "Liveness Check Passed",
        "liveness_failed": "Liveness Check Failed",
        "no_errors": "No validation errors found",
        "processing": "Processing, please wait...",
    },
    "hi": {
        "title": "एआई दस्तावेज़ जांच प्रणाली",
        "upload_doc": "दस्तावेज़ अपलोड करें",
        "upload_live": "लाइव फोटो अपलोड / कैप्चर करें",
        "analyze": "विश्लेषण करें",
        "risk_score": "जोखिम स्कोर",
        "face_match": "चेहरा मिलान",
        "tamper_score": "छेड़छाड़ स्कोर",
        "document_type": "दस्तावेज़ प्रकार",
        "validation_errors": "सत्यापन त्रुटियां",
        "risk_low": "कम जोखिम",
        "risk_medium": "मध्यम जोखिम",
        "risk_high": "उच्च जोखिम",
        "liveness_passed": "लाइवनेस जांच पास हुई",
        "liveness_failed": "लाइवनेस जांच विफल",
        "no_errors": "कोई सत्यापन त्रुटि नहीं मिली",
        "processing": "संसाधित किया जा रहा है, कृपया प्रतीक्षा करें...",
    },
}


def get_text(key: str, lang: str = "en") -> str:
    """Return the translated text for `key`, falling back to English."""
    lang = lang if lang in translations else "en"
    return translations[lang].get(key, translations["en"].get(key, key))


if __name__ == "__main__":
    print(get_text("title", "en"))
    print(get_text("title", "hi"))
    print(get_text("risk_high", "hi"))
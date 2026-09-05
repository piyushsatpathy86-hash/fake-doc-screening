"""
modules/qr_verify.py
Reads a QR code image and checks whether its decoded content matches
the expected `data` (string or dict), used to confirm a printed/
displayed QR code hasn't been swapped or edited.
"""

import json
import cv2


def _decode_qr(qr_path: str):
    """Decode a QR code image and return its string content, or None."""
    image = cv2.imread(qr_path)
    if image is None:
        return None

    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(image)

    return data if data else None


def verify_qr(qr_path: str, data) -> bool:
    """
    Returns True if the QR code at `qr_path` decodes to content that
    matches `data` (a string, or a dict which will be JSON-compared).
    """
    decoded = _decode_qr(qr_path)
    if decoded is None:
        return False

    if isinstance(data, dict):
        try:
            decoded_dict = json.loads(decoded)
            return decoded_dict == data
        except (json.JSONDecodeError, TypeError):
            return False

    return decoded == data


if __name__ == "__main__":
    sample_data = {
        "passport_number": "A1234567",
        "risk_level": "LOW",
        "blockchain_hash": "abcd1234efgh5678",
    }
    print(verify_qr("sample_qr.png", sample_data))
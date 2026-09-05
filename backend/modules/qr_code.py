"""
modules/qr_code.py
Generates a QR code image encoding a screening result summary,
so an officer can quickly scan and verify a document's status.
"""

import qrcode
import json


def generate_qr(data, output_path: str = "qr_code.png") -> str:
    """
    Generate a QR code image from `data` (a string, or a dict which
    will be JSON-encoded) and save it to `output_path`.
    Returns the output path.
    """
    if isinstance(data, dict):
        data = json.dumps(data, default=str)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return output_path


if __name__ == "__main__":
    sample_data = {
        "passport_number": "A1234567",
        "risk_level": "LOW",
        "blockchain_hash": "abcd1234efgh5678",
    }
    print(generate_qr(sample_data, "sample_qr.png"))
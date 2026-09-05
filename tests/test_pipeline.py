"""
tests/test_pipeline.py
Runs the full screening pipeline over every image found in
data/sample_images/ and prints the results. Useful for a quick
manual smoke-test of the whole system without using the API.

Usage:
    python tests/test_pipeline.py
"""

import os
import sys

# Make backend/ and backend/modules/ importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "backend"))
sys.path.append(os.path.join(BASE_DIR, "backend", "modules"))

from modules import ocr, validation, document_type, tamper, noise_analysis, risk  # noqa: E402

SAMPLE_DIR = os.path.join(BASE_DIR, "data", "sample_images")


def run_pipeline_on_image(image_path: str):
    print(f"\n--- Processing: {os.path.basename(image_path)} ---")

    fields = ocr.extract_fields(image_path)
    print("Fields:", fields)

    errors = validation.validate_document(fields)
    print("Validation errors:", errors)

    doc_type = document_type.detect_document_type(image_path)
    print("Document type:", doc_type)

    tamper_score, _ = tamper.detect_tampering(image_path)
    print("Tamper score:", tamper_score)

    noise_score = noise_analysis.analyze_noise(image_path)
    print("Noise score:", noise_score)

    # Face match / liveness require a second (live) image, so we skip
    # them here and just demonstrate the risk calculation with mock values.
    risk_result = risk.calculate_risk(
        validation_errors=errors,
        tamper_score=tamper_score,
        face_match=True,
        liveness_passed=True,
    )
    print("Risk result:", risk_result)


def main():
    if not os.path.isdir(SAMPLE_DIR):
        print(f"Sample image directory not found: {SAMPLE_DIR}")
        print("Create it and add some .jpg/.png test documents.")
        return

    images = [
        f for f in os.listdir(SAMPLE_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not images:
        print(f"No sample images found in {SAMPLE_DIR}")
        return

    for image_name in images:
        run_pipeline_on_image(os.path.join(SAMPLE_DIR, image_name))


if __name__ == "__main__":
    main()
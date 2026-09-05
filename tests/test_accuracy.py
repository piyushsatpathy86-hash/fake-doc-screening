"""
tests/test_accuracy.py
Calculates basic accuracy metrics (True Positive Rate / False Positive
Rate) for the risk classifier, given a labeled test set.

Expected labeled data format: a list of tuples
    (image_path, is_actually_fake: bool)
For a real evaluation, replace `LABELED_SAMPLES` below with your own
labeled dataset (e.g. loaded from a CSV file).

Usage:
    python tests/test_accuracy.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "backend"))
sys.path.append(os.path.join(BASE_DIR, "backend", "modules"))

from modules import ocr, validation, tamper, risk  # noqa: E402

SAMPLE_DIR = os.path.join(BASE_DIR, "data", "sample_images")

# Example labeled dataset: (filename, is_actually_fake)
# Update this list to match your real sample_images + known ground truth.
LABELED_SAMPLES = [
    # ("genuine_passport_1.jpg", False),
    # ("fake_passport_1.jpg", True),
]

RISK_THRESHOLD_FOR_FAKE = 60  # risk_score above this => predicted "fake"


def predict_is_fake(image_path: str) -> bool:
    """Run the pipeline (minus face/liveness) and predict fake/genuine."""
    fields = ocr.extract_fields(image_path)
    errors = validation.validate_document(fields)
    tamper_score, _ = tamper.detect_tampering(image_path)

    result = risk.calculate_risk(
        validation_errors=errors,
        tamper_score=tamper_score,
        face_match=True,       # assume verified for this offline test
        liveness_passed=True,  # assume verified for this offline test
    )
    return result["risk_score"] >= RISK_THRESHOLD_FOR_FAKE


def calculate_metrics(labeled_samples):
    """
    Returns a dict with true_positive_rate, false_positive_rate, and
    the raw confusion-matrix counts.
    """
    true_positives = 0   # predicted fake, actually fake
    false_negatives = 0  # predicted genuine, actually fake
    false_positives = 0  # predicted fake, actually genuine
    true_negatives = 0   # predicted genuine, actually genuine

    for filename, is_actually_fake in labeled_samples:
        image_path = os.path.join(SAMPLE_DIR, filename)
        if not os.path.exists(image_path):
            print(f"Skipping missing file: {filename}")
            continue

        predicted_fake = predict_is_fake(image_path)

        if is_actually_fake and predicted_fake:
            true_positives += 1
        elif is_actually_fake and not predicted_fake:
            false_negatives += 1
        elif not is_actually_fake and predicted_fake:
            false_positives += 1
        else:
            true_negatives += 1

    total_fake = true_positives + false_negatives
    total_genuine = false_positives + true_negatives

    tpr = round(true_positives / total_fake, 4) if total_fake else 0.0
    fpr = round(false_positives / total_genuine, 4) if total_genuine else 0.0

    return {
        "true_positive_rate": tpr,
        "false_positive_rate": fpr,
        "true_positives": true_positives,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
    }


def main():
    if not LABELED_SAMPLES:
        print("LABELED_SAMPLES is empty. Add (filename, is_actually_fake) "
              "tuples pointing to files in data/sample_images/ to run this test.")
        return

    metrics = calculate_metrics(LABELED_SAMPLES)
    print("Accuracy metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
"""
modules/tamper.py
Error Level Analysis (ELA) based tamper detection.
Idea: re-save the image at a known JPEG quality and compare it to the
original. Areas that were edited/pasted tend to compress differently
than untouched areas, showing up as bright spots in the difference.
"""

import os
import cv2
import numpy as np


def detect_tampering(image_path: str, output_dir: str = "uploads"):
    """
    Returns
    -------
    tamper_score : float  (0-1, higher = more likely tampered)
    heatmap : numpy.ndarray (BGR image, same size as input) or None
    """
    if not os.path.exists(image_path):
        return 0.0, None

    image = cv2.imread(image_path)
    if image is None:
        return 0.0, None

    os.makedirs(output_dir, exist_ok=True)
    temp_path = os.path.join(output_dir, "_ela_temp.jpg")

    # Re-compress at quality 90 and compare
    cv2.imwrite(temp_path, image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    recompressed = cv2.imread(temp_path)

    if recompressed is None or recompressed.shape != image.shape:
        recompressed = cv2.resize(recompressed, (image.shape[1], image.shape[0])) \
            if recompressed is not None else image.copy()

    diff = cv2.absdiff(image, recompressed)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Amplify small differences so they're visible / measurable
    amplified = cv2.convertScaleAbs(gray_diff, alpha=10)

    threshold = 25
    suspicious_pixels = int(np.sum(amplified > threshold))
    total_pixels = amplified.size
    tamper_score = round(suspicious_pixels / total_pixels, 4) if total_pixels else 0.0
    tamper_score = min(tamper_score, 1.0)

    heatmap = cv2.applyColorMap(amplified, cv2.COLORMAP_JET)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return tamper_score, heatmap


if __name__ == "__main__":
    score, heatmap = detect_tampering("sample_passport.jpg")
    print("Tamper score:", score)
    if heatmap is not None:
        cv2.imwrite("heatmap_output.jpg", heatmap)
        print("Heatmap saved to heatmap_output.jpg")
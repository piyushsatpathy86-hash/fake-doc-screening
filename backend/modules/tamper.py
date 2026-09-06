"""
modules/tamper.py
Tamper detection using Error Level Analysis (ELA) + connected-component
blob scoring.

Why blob scoring instead of a raw "% of high-error pixels" count:
A genuine edit (copy-paste, retouch, splice) shows up in ELA as a
spatially LOCALIZED blob of high error. But if the source image was
never JPEG-compressed to begin with (e.g. a PNG screenshot or a
synthetically generated test document), re-saving it as JPEG for the
ELA diff introduces a roughly UNIFORM layer of compression noise
across the WHOLE image -- lots of scattered high-value pixels, but
no single connected region. A raw pixel-count ratio can't tell these
two situations apart and saturates to 1.0 on both. Connected-component
analysis can: after thresholding, a morphological "open" (erode then
dilate) wipes out small scattered noise specks but leaves large
connected regions intact, so we score off the size of the largest
surviving blob, not the raw pixel count.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageChops

# JPEG quality used for the ELA re-save. 90 is a common default;
# tune against your labeled sample set if scores look off.
ELA_QUALITY = 90

# Kernel size for the morphological open/close pass. Bigger = more
# aggressive noise removal, but can also erase genuinely small edits.
MORPH_KERNEL_SIZE = 5

# Scales the largest-blob area ratio into a 0-1 tamper score.
# Empirically tuned starting point -- re-tune against your own
# labeled genuine/fake sample set (tests/test_accuracy.py).
SCORE_SCALE_FACTOR = 12.0


def _error_level_analysis(image_path: str, quality: int = ELA_QUALITY) -> np.ndarray:
    """
    Returns a single-channel (grayscale) numpy array the same size
    as the input image, where brighter pixels indicate a larger
    difference between the original and its JPEG re-save at
    `quality` -- i.e. a higher likelihood that region was edited
    after the original capture/scan.
    """
    original = Image.open(image_path).convert("RGB")

    tmp_path = image_path + "_ela_tmp.jpg"
    try:
        original.save(tmp_path, "JPEG", quality=quality)
        resaved = Image.open(tmp_path)

        diff = ImageChops.difference(original, resaved)

        extrema = diff.getextrema()  # ((minR,maxR),(minG,maxG),(minB,maxB))
        max_diff = max(channel_max for _, channel_max in extrema)
        if max_diff == 0:
            max_diff = 1  # avoid div-by-zero on a perfectly flat diff

        scale = 255.0 / max_diff
        diff = Image.eval(diff, lambda x: x * scale)

        return np.array(diff.convert("L"))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _largest_blob_area_ratio(ela_map: np.ndarray):
    """
    Thresholds the ELA map with Otsu (auto-adapts per image, no manual
    magic number), strips small scattered noise with a morphological
    open, then returns the ratio of the LARGEST remaining connected
    region's area to the total image area. Also returns a binary
    mask (for the heatmap) with only the surviving blobs highlighted.
    """
    # Otsu picks a threshold automatically from the image's own
    # brightness histogram -- adapts per-document instead of using one
    # fixed number for every image.
    _, binary = cv2.threshold(ela_map, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)
    # Open: erode then dilate -- wipes out small isolated noise specks
    # (the kind uniform JPEG re-compression noise produces) while
    # leaving large connected regions (the kind a real edit produces)
    # intact.
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    # Close: dilate then erode -- fills small gaps inside a real
    # edited region so it counts as one blob, not several small ones.
    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0.0, cleaned

    largest_area = max(cv2.contourArea(c) for c in contours)
    total_area = ela_map.shape[0] * ela_map.shape[1]
    ratio = largest_area / total_area if total_area else 0.0

    return ratio, cleaned


def detect_tampering(image_path: str, output_dir: str = "uploads"):
    """
    Returns
    -------
    tamper_score : float  -- 0-1, higher = more likely edited/tampered
    heatmap : np.ndarray or None -- BGR image highlighting the
              surviving high-error blob(s), for display in the frontend
    """
    if not os.path.exists(image_path):
        return 0.0, None

    try:
        ela_map = _error_level_analysis(image_path)
    except Exception:
        # Corrupt image, unsupported format, etc. -- fail safe to 0
        # rather than crashing the whole /upload pipeline.
        return 0.0, None

    if ela_map.size == 0:
        return 0.0, None

    area_ratio, blob_mask = _largest_blob_area_ratio(ela_map)
    tamper_score = round(min(area_ratio * SCORE_SCALE_FACTOR, 1.0), 4)

    # Heatmap: base image dimmed down, with only the surviving blob(s)
    # painted red -- so a genuine document (where the mask ends up
    # mostly empty after the open/close pass) shows a mostly-clean
    # heatmap instead of the whole card lighting up.
    heatmap = cv2.cvtColor(ela_map, cv2.COLOR_GRAY2BGR)
    heatmap = (heatmap * 0.3).astype(np.uint8)  # dim the base ELA view
    heatmap[blob_mask > 0] = (0, 0, 255)

    return tamper_score, heatmap


if __name__ == "__main__":
    score, heatmap_img = detect_tampering("sample_passport.jpg")
    print("Tamper score:", score)
    if heatmap_img is not None:
        cv2.imwrite("sample_tamper_heatmap.jpg", heatmap_img)
        print("Heatmap saved to sample_tamper_heatmap.jpg")
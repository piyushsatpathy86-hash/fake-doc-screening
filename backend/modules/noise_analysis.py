"""
modules/noise_analysis.py
Analyzes sensor noise patterns to help detect image splicing.
Idea: genuine camera photos have a fairly uniform noise pattern
across the whole image. If part of the image was copy-pasted from
a different source, its local noise level often differs noticeably
from the surrounding area.
"""

import os
import cv2
import numpy as np


def analyze_noise(image_path: str) -> float:
    """
    Returns noise_score (0-1). Higher score = more inconsistent noise
    across the image, which is a signal of possible splicing/editing.
    """
    if not os.path.exists(image_path):
        return 0.0

    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0.0

    # Denoise the image, then isolate the noise = original - denoised
    denoised = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
    noise = cv2.absdiff(image, denoised)

    # Split the noise map into a grid of blocks and measure noise
    # variance in each block. High variance BETWEEN blocks suggests
    # inconsistent noise (possible tampering).
    block_size = 32
    h, w = noise.shape
    block_means = []

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block = noise[y:y + block_size, x:x + block_size]
            block_means.append(float(np.mean(block)))

    if not block_means:
        return 0.0

    block_means = np.array(block_means)
    # Coefficient of variation as a simple inconsistency measure
    mean_val = np.mean(block_means)
    std_val = np.std(block_means)

    if mean_val == 0:
        return 0.0

    noise_score = std_val / mean_val
    # Normalize into a rough 0-1 range (empirically tuned cap)
    noise_score = min(noise_score / 2.0, 1.0)

    return round(float(noise_score), 4)


if __name__ == "__main__":
    print("Noise score:", analyze_noise("sample_passport.jpg"))
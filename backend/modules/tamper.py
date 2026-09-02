import cv2
import numpy as np

def detect_tampering(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return 0.0, np.zeros((100, 100, 3), dtype=np.uint8)
    return 0.1, img
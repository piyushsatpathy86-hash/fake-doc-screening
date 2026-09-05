"""
modules/liveness.py
Basic liveness check using blink / eye-openness detection via OpenCV's
Haar cascades. This is a lightweight prototype-level check - it looks
at a single image and estimates whether eyes are detected/open, which
is a weak proxy for "this is a live person, not a printed photo".

For a stronger liveness check, use a sequence of video frames and
measure the Eye Aspect Ratio (EAR) over time to detect an actual blink.
"""

import os
import cv2

EYE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_eye.xml"
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def check_liveness(image_path: str) -> bool:
    """
    Returns True if a face AND at least one open eye are detected,
    which is used here as a simple stand-in for "liveness_passed".
    """
    if not os.path.exists(image_path):
        return False

    image = cv2.imread(image_path)
    if image is None:
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
    eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return False

    for (x, y, w, h) in faces:
        face_region = gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(face_region, scaleFactor=1.1, minNeighbors=5)
        if len(eyes) >= 1:
            return True

    return False


if __name__ == "__main__":
    print("Liveness passed:", check_liveness("live_photo.jpg"))
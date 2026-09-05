"""
modules/video_capture.py
Grabs a single frame from a webcam. In this prototype it's a mock/
best-effort implementation: it tries to open the default camera and
grab one frame; if no camera is available (e.g. running on a server),
it returns None so callers can fall back to file upload instead.
"""

import cv2


def capture_frame(save_path: str = "captured_frame.jpg", camera_index: int = 0):
    """
    Try to capture a single frame from the webcam and save it to
    `save_path`. Returns the path on success, or None if no camera
    is available / capture failed.
    """
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            cap.release()
            return None

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return None

        cv2.imwrite(save_path, frame)
        return save_path
    except Exception:
        return None


if __name__ == "__main__":
    path = capture_frame()
    if path:
        print(f"Frame captured and saved to {path}")
    else:
        print("No camera available (expected on servers/CI). "
              "Use frontend camera capture (getUserMedia) instead.")
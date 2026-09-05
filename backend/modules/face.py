"""
modules/face.py
Compares the face photo on the document with a live selfie to confirm
the person presenting the ID is who they claim to be, using DeepFace.
"""

import os

try:
    from deepface import DeepFace
except ImportError:
    DeepFace = None


def verify_face(doc_path: str, live_path: str):
    """
    Returns
    -------
    match : bool       - whether DeepFace considers the faces the same person
    similarity : float - 0-1 similarity score (higher = more similar)
    """
    if DeepFace is None:
        return False, 0.0

    if not os.path.exists(doc_path) or not os.path.exists(live_path):
        return False, 0.0

    try:
        result = DeepFace.verify(
            img1_path=doc_path,
            img2_path=live_path,
            model_name="VGG-Face",
            enforce_detection=False,
        )
        distance = result.get("distance", 1.0)
        similarity = round(max(0.0, 1 - distance), 4)
        match = bool(result.get("verified", False))
        return match, similarity
    except Exception:
        return False, 0.0


if __name__ == "__main__":
    match, similarity = verify_face("document_face.jpg", "live_photo.jpg")
    print("Match:", match, "Similarity:", similarity)
import cv2

def check_liveness(image_path):
    """
    Simple liveness check based on image sharpness.
    Blurry image = suspicious/fake print. Sharp image = likely real/live.
    """
    image = cv2.imread(image_path)
    if image is None:
        return {"is_live": False, "reason": "Image not readable"}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_sharp = sharpness > 50

    return {
        "is_live": bool(is_sharp),
        "sharpness_score": round(sharpness, 2)
    }


if __name__ == "__main__":
    result = check_liveness("data/sample_images/live_photo.jpg")
    print(result)
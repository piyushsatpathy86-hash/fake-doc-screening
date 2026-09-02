from deepface import DeepFace

def compare_faces(document_image_path, live_image_path):
    try:
        result = DeepFace.verify(
            img1_path=document_image_path,
            img2_path=live_image_path,
            model_name="Facenet",
            detector_backend="skip",
            enforce_detection=False
        )
        match_percent = round((1 - result["distance"]) * 100, 2)
        if match_percent < 0:
            match_percent = 0

        return {
            "is_match": result["verified"],
            "match_percent": match_percent,
            "distance": round(result["distance"], 4)
        }
    except Exception as e:
        return {
            "is_match": False,
            "match_percent": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    output = compare_faces("data/sample_images/passport_photo.jpg", "data/sample_images/live_photo.jpg")
    print(output)
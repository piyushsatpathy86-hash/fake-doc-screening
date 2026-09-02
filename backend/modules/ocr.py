# ocr.py
# Ye file passport image se text nikalti hai (naam, passport number, date, etc.)

from passporteye import read_mrz
import pytesseract
from PIL import Image
import cv2

# Windows users: agar tesseract path set nahi hai to ye line uncomment karo aur apna path daalo
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_mrz_data(image_path):
    """
    Ye function passport ki MRZ (Machine Readable Zone) - passport ke neeche wali 
    2 lines - padhta hai. Isme naam, passport number, expiry date hota hai.
    """
    try:
        mrz = read_mrz(image_path)
        
        if mrz is None:
            return {
                "success": False,
                "message": "MRZ nahi mila. Image clear nahi hai ya passport nahi hai."
            }
        
        mrz_data = mrz.to_dict()
        
        result = {
            "success": True,
            "surname": mrz_data.get("surname", ""),
            "given_names": mrz_data.get("names", ""),
            "passport_number": mrz_data.get("number", ""),
            "nationality": mrz_data.get("nationality", ""),
            "date_of_birth": mrz_data.get("date_of_birth", ""),
            "expiration_date": mrz_data.get("expiration_date", ""),
            "sex": mrz_data.get("sex", ""),
            "country": mrz_data.get("country", ""),
            "mrz_valid_score": mrz_data.get("valid_score", 0)
        }
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error aaya: {str(e)}"
        }


def extract_full_text(image_path):
    """
    Ye function pure passport image se saara text nikalta hai
    (sirf MRZ nahi, poora passport)
    """
    try:
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray_image)
        
        return {
            "success": True,
            "full_text": text
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error aaya: {str(e)}"
        }


# Test karne ke liye (isko seedha run kar sakte ho)
if __name__ == "__main__":
    test_image = "sample_passport.jpg"  # apni test image ka naam yaha daalo
    
    print("--- MRZ Data ---")
    print(extract_mrz_data(test_image))
    
    print("\n--- Full Text ---")
    print(extract_full_text(test_image))

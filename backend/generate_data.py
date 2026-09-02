from PIL import Image, ImageDraw
import random
import os

os.makedirs("data/sample_images", exist_ok=True)

names = ["John Doe", "Jane Smith", "Raj Kumar", "Priya Sharma", "Alex Brown", "Maria Garcia"]

def generate_passport(index, tampered=False, tamper_type=None):
    img = Image.new('RGB', (600, 400), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    
    passport_no = f"{chr(random.randint(65,90))}{random.randint(1000000,9999999)}"
    
    draw.rectangle([20, 20, 200, 220], outline="black", width=2)
    draw.text((30, 30), "PASSPORT", fill="black")
    draw.text((30, 60), f"Name: {random.choice(names)}", fill="black")
    draw.text((30, 90), f"Passport No: {passport_no}", fill="black")
    draw.text((30, 120), f"DOB: {random.randint(1,28)}/{random.randint(1,12)}/{random.randint(1970,2000)}", fill="black")
    
    if tampered and tamper_type == "date":
        draw.text((30, 150), "Expiry: 01/01/2020", fill="red")
    else:
        draw.text((30, 150), f"Expiry: {random.randint(1,28)}/{random.randint(1,12)}/{random.randint(2026,2035)}", fill="black")
    
    draw.text((30, 180), "Nationality: IND", fill="black")
    
    draw.rectangle([250, 40, 450, 200], outline="black", width=2)
    
    if tampered and tamper_type == "photo":
        draw.rectangle([250, 40, 450, 200], outline="red", width=3)
        draw.text((300, 100), "TAMPERED", fill="red")
    else:
        draw.text((300, 100), "PHOTO", fill="gray")
    
    draw.text((20, 300), "P<IND<<JOHN<DOE<<<<<<<<<<<<<<<<<<<<<<<<<<", fill="black")
    draw.text((20, 330), f"{passport_no}<3IND8501011M3001011<<<<<<<<<<<<<<<<", fill="black")
    
    if tampered and tamper_type == "stamp":
        draw.ellipse([400, 250, 550, 350], outline="red", width=2)
        draw.text((430, 280), "FAKE", fill="red")
    
    if tampered:
        filename = f"data/sample_images/tampered_{tamper_type}_{index:03d}.jpg"
    else:
        filename = f"data/sample_images/genuine_{index:03d}.jpg"
    
    img.save(filename)
    print(f"Generated: {filename}")

# Generate 30 genuine
for i in range(30):
    generate_passport(i)

# Generate 20 tampered
for i in range(7):
    generate_passport(30+i, tampered=True, tamper_type="photo")
for i in range(7):
    generate_passport(37+i, tampered=True, tamper_type="date")
for i in range(6):
    generate_passport(44+i, tampered=True, tamper_type="stamp")

print("Data generation complete!")
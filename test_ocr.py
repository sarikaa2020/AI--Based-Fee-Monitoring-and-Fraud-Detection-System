import pytesseract
import cv2
import re

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load image
img = cv2.imread("sample.jpg.jpeg")

if img is None:
    print("❌ Image not loaded")
else:
    print("✅ Image loaded")

    # OCR
    text = pytesseract.image_to_string(img)

    print("\n📄 Extracted Text:")
    print(text)

    # Fee detection
    text_lower = text.lower()

    if "tuition" in text_lower:
        fee_type = "Tuition Fee"
    elif "bus" in text_lower:
        fee_type = "Bus Fee"
    elif "placement" in text_lower:
        fee_type = "Placement Fee"
    elif "skill" in text_lower:
        fee_type = "Skill Fee"
    else:
        fee_type = "Unknown"

    print("\n🎯 Fee Type:", fee_type)

    # Amount detection
    amounts = re.findall(r'\d[\d,]*', text)

    clean_amounts = []

    for amt in amounts:
        amt_clean = amt.replace(",", "")

        if amt_clean.isdigit():
            value = int(amt_clean)

            if 100 <= value <= 10000:
                clean_amounts.append(str(value))

    print("\n💰 Amounts:", clean_amounts)
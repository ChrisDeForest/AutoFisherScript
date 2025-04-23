import pytesseract
from PIL import Image, ImageFilter
import re
import logging
import os

last_processed_ocr = ""

def detect_possible_captcha_and_classify(driver):
    global last_processed_ocr

    try:
        # Ensure assets folder exists
        os.makedirs("assets", exist_ok=True)

        driver.save_screenshot("assets/screen.png")
        image = Image.open("assets/screen.png")
        image.filter(ImageFilter.SHARPEN)
        gray = image.convert("L")
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

        # OPTIONAL: crop image to suspected captcha area
        captcha_region = image.crop((575, 650, 1470, 1210))  # adjust this (use gray.crop() if doing image captchas)
        captcha_region.save("assets/cropped.png")

        # Run OCR on it
        # text = pytesseract.image_to_string(captcha_region, config=custom_config).strip()
        text = pytesseract.image_to_string(captcha_region).strip()    # todo choose one or other
        if not text or text == last_processed_ocr:
            print("TEST1")
            return "unknown", None

        last_processed_ocr = text
        text_lower = text       # todo put .lower() back if this doesn't work. code was correct but lowercase

        logging.debug(f"OCR result:\n{text}")

        # Classify message
        if "/verify" in text_lower or "captcha" in text_lower or "Please use /verify" in text_lower:
            logging.info("Classified message as CAPTCHA.")
            print(text_lower)
            code = extract_code_from_text(text)
            if code:
                with open("assets/captcha_text.txt", "w", encoding="utf-8") as f:
                    f.write(text)
            return "captcha", code
        elif "/fish" in text_lower or "you caught" in text_lower:
            logging.info("Classified message as FISH.")
            return "fish", None
        elif "/farm" in text_lower or "you farmed" in text_lower:
            logging.info("Classified message as FARMED.")
            return "farmed", None
        return "unknown", None

    except Exception as e:
        logging.error(f"[captcha classification error] {e}")
        return "unknown", None

def extract_code_from_text(text):
    text = text.strip()     # todo put .lower() back if this doesn't work

    # Match /verify followed by a valid code, but not if it's 'regen'
    match = re.search(r"/verify\s+((?!regen\b)[a-zA-Z0-9]{4,})", text)
    if match:
        return match.group(1)

    # Match Code: <something> — still allow that
    match = re.search(r"code:\s*([a-zA-Z0-9]{4,})", text)
    if match:
        return match.group(1)

    return None


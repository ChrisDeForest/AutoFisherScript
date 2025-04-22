import logging, re
from PIL import Image
from selenium.webdriver import Keys

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def solve_captcha(driver):
    driver.save_screenshot("assets/screen.png")
    image = Image.open("assets/screen.png")

    # OPTIONAL: crop image to suspected captcha area
    captcha_region = image.crop((575, 650, 1470, 1210))  # adjust this
    captcha_region.save("assets/cropped.png")

    text = pytesseract.image_to_string(captcha_region)
    # logging.info(f"TEXT EXTRACTED: {text}") # todo remove just for testing
    print(f"TEXT:  {text}") # todo remove just for testing
    code = extract_code(text)
    # logging.info(f"CODE EXTRACTED: {code}") # todo remove just for testing
    print(f"CODE: {code}") # todo remove just for testing

    if code:
        logging.info(f"Captcha solved: {code}")
        try:
            input_box = driver.find_element("xpath", '//div[@role="textbox"]')
            input_box.send_keys(f"/verify {code}")
            input_box.send_keys("\n")
            input_box.send_keys(Keys.RETURN)
        except Exception as e:
            logging.error(f"Failed to send captcha solution: {e}")
    else:
        logging.warning("Captcha code not detected.")

def extract_code(text):
    # Normalize spacing and case
    text = text.strip()

    # First, look for: /verify CODE
    verify_match = re.search(r"/verify\s+([A-Za-z0-9]{4,})", text)
    if verify_match:
        return verify_match.group(1)

    # If not found, try: Code: CODE
    code_match = re.search(r"Code:\s*([A-Za-z0-9]{4,})", text, re.IGNORECASE)
    if code_match:
        return code_match.group(1)

    # Nothing found
    return None


import pytesseract
from PIL import Image
import re, os, logging
import ollama, base64

last_processed_ocr = ""

def classify_message(driver, type="captcha") -> str:
    global last_processed_ocr

    try:
        # Ensure assets folder exists
        os.makedirs("assets", exist_ok=True)

        driver.save_screenshot("assets/screen.png")
        image = Image.open("assets/screen.png")
        cropped_region = ""
        if type == "captcha":
            cropped_region = image.crop((575, 275, 1475, 1200))     # cropped for large captcha message
            cropped_region.save("assets/captcha.png")
        elif type == "message":
            cropped_region = image.crop((575, 1025, 1475, 1200))    # cropped for smaller verification message
            cropped_region.save("assets/message.png")

        # Run OCR on it
        text = pytesseract.image_to_string(cropped_region).strip()

        if not text:    # classifying message
            logging.info("No OCR result")
            return "unknown"
        elif text == last_processed_ocr and not type == "message":
            logging.info("Classified message as DUPLICATE")
            print(text)
            return "duplicate"

        last_processed_ocr = text   # put this AFTER duplicate detection to avoid flagging everything as duplicate

        if ("You may now continue." in text or "continue." in text or
             "You currently do not have" in text or "currently" in text):
            logging.info("Classified message as SUCCESSFUL CAPTCHA")
            return "success"
        elif "/verify" in text or "captcha" in text or "Please use /verify" in text:
            logging.info("Classified message as CAPTCHA.")
            return "captcha"
        elif "/fish" in text or "you caught" in text:
            logging.info("Classified message as FISH.")
            return "fish"
        elif "/farm" in text or "you farmed" in text:
            logging.info("Classified message as FARMED.")
            return "farmed"

        return "unknown"    # default back to unknown

    except Exception as e:
        logging.error(f"[captcha classification error] {e}")
        return "error"


def get_captcha_code():
    # Encode the image to base64
    with open('assets/captcha.png', 'rb') as img_file:
        image_bytes = img_file.read()
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    # Send the image to the vision model
    response = ollama.chat(
        model='llama3.2-vision:11b',
        messages=[
            {
                'role': 'user',
                'content': 'What is the captcha code in this image? Return only the code with no special characters.'
                           'If no code could be identified, return "NO CODE FOUND"',
                'images': [encoded_image],
            }
        ]
    )
    # using regex to remove special chars
    response = re.sub('[^A-Za-z0-9]+', '', response['message']['content'])
    return response.strip()

def extract_code_from_text(text):
    text = text.strip()
    match = re.search(r"/verify\s+((?!\b(?:regen|command)\b)[a-zA-Z0-9]{4,})", text)
    if match:   # Match /verify followed by a valid code, but NOT 'regen' or 'command'
        return match.group(1)
    match = re.search(r"code:\s*([a-zA-Z0-9]{4,})", text)
    if match:   # Match Code: <something> — still allow that
        return match.group(1)
    return None


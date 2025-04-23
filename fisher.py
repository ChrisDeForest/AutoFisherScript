from selenium.common import NoSuchElementException
from selenium.webdriver import Keys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from captcha import detect_possible_captcha_and_classify
import time, keyboard, logging

is_paused = False
last_captcha_text = ""
FISHING_COOLDOWN = 3        # change this to closer to your actual fishing cooldown
MODE = "fishing"            # change this depending on what bot you are using

def start_fishing():
    # Setup browser
    service = Service('C:/Users/Chris/Downloads/chromedriver-win64/chromedriver.exe')  # your correct path
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=D:/Coding Projects/PycharmProjects/AutoFisherScript/chrome_profile")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://discord.com/channels/@me")

    logging.info("Waiting for manual login...")
    input("Log in to Discord manually and press Enter here to start...")

    logging.info("Looking for message input box...")
    input_box = None
    while input_box is None:
        try:
            input_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
            logging.info("Found message input box!")
        except NoSuchElementException:
            time.sleep(1)

    keyboard.add_hotkey('ctrl+alt+p', toggle_pause)
    logging.info("Press CTRL+ALT+P at any time to pause/resume the loop.")

    logging.info(f"Starting {MODE} loop.")

    pause_logged = False

    while True:
        if is_paused:
            if not pause_logged:
                logging.info("Bot is paused. Waiting... Press Ctrl+Alt+P to resume.")
                pause_logged = True
            time.sleep(1)
            continue
        else:
            pause_logged = False
        try:
            # Only act if we're in the right DM
            if not is_in_virtual_chat(driver):
                logging.debug(f"Not in Virtual {MODE[:4]}er DM — waiting...")
                time.sleep(5)
                continue

            # In your loop:
            msg_type, code = detect_possible_captcha_and_classify(driver)

            if msg_type == "captcha":
                logging.warning(f"Captcha detected! Code: {code if code else '???'}")
                if code:
                    input_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
                    input_box.send_keys(f"/verify {code}")
                    input_box.send_keys("\n")
                print(f"Captcha detected! Code: {code if code else '???'}")
                time.sleep(5)
                continue

            # Send /fish
            input_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
            if MODE == "fishing":
                input_box.send_keys("/fish")
            elif MODE == "farming":
                input_box.send_keys("/farm")
            input_box.send_keys(Keys.ENTER)
            input_box.send_keys(Keys.ENTER)
            logging.info(f"Sent /{MODE[:4]}")

            time.sleep(FISHING_COOLDOWN)

        except Exception as e:
            logging.debug(f"[loop retrying] {e.__class__.__name__}: {e}")
            time.sleep(2)


def is_in_virtual_chat(driver):
    try:
        # Looks for the div with an aria-label like "Virtual Fisher#7036"
        vf_element = ""
        if MODE == "fishing":
            vf_element = driver.find_element(By.XPATH, '//div[@aria-label="Virtual Fisher#7036"]')
        elif MODE == "farming":
            vf_element = driver.find_element(By.XPATH, '//div[@aria-label="Virtual Farmer#6004"]')
        return vf_element.text.strip().lower() == "virtual fisher" or vf_element.text.strip().lower() == "virtual farmer"
    except Exception as e:
        logging.debug(f"[channel context check failed] {e}")
        return False


def toggle_pause():
    global is_paused
    is_paused = not is_paused
    state = "Paused" if is_paused else "Resumed"
    logging.info(f"{state} the {MODE} loop.")

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from captcha import solve_captcha
import time, keyboard, logging, datetime

is_paused = False
last_captcha_text = ""
FISHING_COOLDOWN = 3.75     # change this to closer to your actual fishing cooldown

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

    logging.info("Starting fishing loop.")

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
            if not is_in_virtual_fisher_chat(driver):
                logging.debug("Not in Virtual Fisher DM — waiting...")
                time.sleep(5)
                continue

            # Check for captcha
            if detect_possible_captcha(driver):
                logging.warning("⚠️ Captcha detected! Attempting solve...")
                solve_captcha(driver)
                time.sleep(5)
                continue

            # Send /fish
            input_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
            input_box.send_keys("/fish")
            input_box.send_keys("\t")
            input_box.send_keys(Keys.ENTER)
            logging.info("Sent /fish")

            time.sleep(FISHING_COOLDOWN)

        except Exception as e:
            logging.debug(f"[loop retrying] {e.__class__.__name__}: {e}")
            time.sleep(2)


def detect_possible_captcha(driver):
    global last_captcha_text

    try:
        # Get all chat messages
        messages = driver.find_elements(By.XPATH, '//div[@data-list-id="chat-messages"]/div[contains(@class,"messageListItem")]')
        if not messages:
            return False

        # Grab the last message in view
        last_msg = messages[-1]

        # Check for timestamp
        try:
            time_element = last_msg.find_element(By.XPATH, './/time')
            timestamp = time_element.get_attribute("datetime")  # e.g. "2025-04-22T02:59:44.651Z"
            msg_time = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now = datetime.datetime.now(datetime.UTC).replace(tzinfo=datetime.timezone.utc)

            if (now - msg_time).total_seconds() > 20:
                logging.debug("Message is older than 20 seconds, ignoring.")
                return False
        except Exception as e:
            logging.debug(f"Failed to parse timestamp: {e}")
            return False

        # Check for embed inside this message
        embed_elements = last_msg.find_elements(By.XPATH, './/article[contains(@class, "embed")]')
        if not embed_elements:
            return False

        embed = embed_elements[0]
        text = embed.text.strip().lower()

        # Avoid reprocessing the same captcha
        if text == last_captcha_text:
            return False

        last_captcha_text = text

        # Handle confirmation case
        if "you may continue" in text:
            logging.info("Captcha solved! You may continue.")
            return False

        # Detect captcha prompt
        if "captcha" in text or "/verify" in text:
            logging.warning("Captcha detected in most recent message.")
            return True

    except Exception as e:
        logging.debug(f"[captcha detection error] {e}")

    return False



def is_in_virtual_fisher_chat(driver):
    try:
        # Looks for the div with an aria-label like "Virtual Fisher#7036"
        vf_element = driver.find_element(By.XPATH, '//div[@aria-label="Virtual Fisher#7036"]')
        return vf_element.text.strip().lower() == "virtual fisher"
    except Exception as e:
        logging.debug(f"[channel context check failed] {e}")
        return False


def toggle_pause():
    global is_paused
    is_paused = not is_paused
    state = "Paused" if is_paused else "Resumed"
    logging.info(f"{state} the fishing loop.")

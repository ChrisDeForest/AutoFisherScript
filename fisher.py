from selenium.webdriver.chrome.service import Service
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium import webdriver
from datetime import datetime, timedelta

from boost_scheduler import start_boost_scheduler, set_paused_getter, set_command_sender
from captcha import classify_message, get_captcha_code

import time, keyboard, logging

is_paused, pause_logged = False, False
last_captcha_text = ""
FISHING_COOLDOWN = 3        # change this to closer to your actual fishing cooldown
MODE = "fishing"            # change this depending on what bot you are using
last_captcha_solve_time = None
CAPTCHA_GRACE_PERIOD = timedelta(minutes=3)

def start_fishing():
    # Setup browser
    web_driver = setup_browser()
    web_driver.get("https://discord.com/channels/@me")

    logging.info("Waiting for manual login...")
    input("Log in to Discord manually\nEnsure an Ollama vision model is running\nPress enter to start...")

    # Inject dependencies and start boost loop
    # set_paused_getter(lambda: is_paused)
    # set_command_sender(send_command)
    # start_boost_scheduler(driver)

    logging.info("Looking for message input box...")
    input_box = None
    while input_box is None:
        try:
            input_box = web_driver.find_element(By.XPATH, '//div[@role="textbox"]')
            logging.info("Found message input box!")
        except NoSuchElementException:
            time.sleep(1)

    keyboard.add_hotkey('ctrl+alt+p', toggle_pause)
    keyboard.add_hotkey('f8', toggle_pause)
    logging.info("Press CTRL+ALT+P or f8 at any time to pause/resume the loop.")

    logging.info(f"Starting {MODE} loop.")

    while True:     # main fishing loop
        if check_is_paused(): continue      # only continue if loop is not paused
        try:
            if not check_right_dm(web_driver=web_driver): continue          # only act if we're in the right DM
            msg_type = classify_message(driver=web_driver, type="captcha")  # check if the bot sent a captcha message
            if msg_type == "captcha":
                code = get_captcha_code()   # get verification code from image
                print("CAPTCHA CODE:", code)    # todo remove just for testing
                if code == "NO CODE FOUND":
                    pause()
                    logging.info("No code found. Waiting for manual captcha solution...")
                    continue
                send_command(web_driver=web_driver, command=f"/verify {code}")  # send verification code
                time.sleep(3)
                msg_type = classify_message(driver=web_driver, type="message")  # check if verification was successful
                if not msg_type == "success":
                    pause()
                    logging.info("Verification failed. Waiting for manual captcha solution...")
                    continue
                # if captcha was successfully solved, skip down a few lines to avoid detection issues
                for i in range(10): send_command(web_driver=web_driver, command=f"Skipping lines: {i + 1}")
            elif msg_type == "duplicate" or msg_type == "error":
                for i in range(5): send_command(web_driver=web_driver, command=f"Skipping lines: {i+1}")
                time.sleep(5)
                continue

            # Send proper command
            if MODE == "fishing":
                send_command(web_driver=web_driver, command="/fish")
            elif MODE == "farming":
                send_command(web_driver=web_driver, command="/farm")

            time.sleep(FISHING_COOLDOWN)

        except Exception as e:
            logging.debug(f"[loop retrying] {e.__class__.__name__}: {e}")
            time.sleep(2)


def is_in_virtual_chat(web_driver):
    try:
        # Looks for the div with an aria-label like "Virtual Fisher#7036" or "Virtual Farmer#6004"
        vf_element = ""
        if MODE == "fishing":
            vf_element = web_driver.find_element(By.XPATH, '//div[@aria-label="Virtual Fisher#7036"]')
        elif MODE == "farming":
            vf_element = web_driver.find_element(By.XPATH, '//div[@aria-label="Virtual Farmer#6004"]')
        return vf_element.text.strip().lower() == "virtual fisher" or vf_element.text.strip().lower() == "virtual farmer"
    except Exception as e:
        logging.debug(f"[channel context check failed] {e}")
        return False

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    state = "Paused" if is_paused else "Resumed"
    logging.info(f"{state} the {MODE} loop.")

def pause():
    global is_paused
    is_paused = True
    logging.info(f"Paused the {MODE} loop.")


def send_command(web_driver, command):
    try:
        input_box = web_driver.find_element(By.XPATH, '//div[@role="textbox"]')
        input_box.send_keys(command)
        input_box.send_keys(Keys.ENTER)
        input_box.send_keys(Keys.ENTER)
        logging.info(f"Sent command: {command}")
    except Exception as e:
        logging.error(f"Failed to send command: {command}. Error: {e}")

def check_right_dm(web_driver) -> bool:
    if not is_in_virtual_chat(web_driver):
        logging.debug(f"Not in Virtual {MODE[:4]}er DM — waiting...")
        time.sleep(5)
        return False
    return True

def check_is_paused() -> bool:
    global pause_logged
    if is_paused:
        if not pause_logged:
            logging.info("Bot is paused. Waiting... Press Ctrl+Alt+P to resume.")
            pause_logged = True
        time.sleep(1)
        return True
    else:
        pause_logged = False
        return False

def setup_browser():
    service = Service('C:/Users/Chris/Downloads/chromedriver-win64/chromedriver.exe')  # path to chrome webdriver
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=D:/Coding Projects/PycharmProjects/AutoFisherScript/chrome_profile")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=service, options=options)

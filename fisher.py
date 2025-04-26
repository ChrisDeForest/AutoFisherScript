from selenium.webdriver.chrome.service import Service
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium import webdriver
from datetime import datetime, timedelta

from boost_scheduler import start_boost_scheduler, set_paused_getter, set_command_sender
from captcha import classify_message, get_captcha_code

import time, keyboard, logging, random

is_paused, pause_logged, is_busy = False, False, False
last_captcha_text = ""
FISHING_COOLDOWN = 3        # change this to closer to your actual fishing cooldown
MODE = "fishing"            # change this depending on what bot you are using
last_captcha_solve_time = None
CAPTCHA_GRACE_PERIOD = timedelta(minutes=3)
last_refresh_time = datetime.now()
REFRESH_INTERVAL = timedelta(minutes=20)

def start_fishing():
    # Setup browser
    web_driver = setup_browser()
    web_driver.get("https://discord.com/channels/@me")

    logging.info("Waiting for manual login...")
    input("Log in to Discord manually\nEnsure an Ollama vision model is running\nPress enter to start...")

    # Inject dependencies and start boost loop
    set_paused_getter(lambda: is_paused)
    set_command_sender(send_command)
    start_boost_scheduler(web_driver)

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
    keyboard.add_hotkey('f12', clear_bot_log)
    logging.info("Press CTRL+ALT+P or f8 at any time to pause/resume the loop.\n" +
                 "Press f12 at any time to clear the log.")

    logging.info(f"Starting {MODE} loop.")

    while True:     # main fishing loop
        maybe_refresh(web_driver=web_driver)
        if check_is_paused(): continue      # only continue if loop is not paused
        try:
            if not check_right_dm(web_driver=web_driver): continue          # only act if we're in the right DM
            msg_type = classify_message(driver=web_driver, type="captcha")  # check if the bot sent a captcha message
            if msg_type == "captcha":
                set_busy(True)      # stop sending other commands while captcha is processing
                code = get_captcha_code()   # get verification code from image
                if code == "NO CODE FOUND":
                    pause()
                    logging.info("No code found. Waiting for manual captcha solution...")
                    set_busy(False)
                    continue
                send_command(web_driver=web_driver, command=f"/verify {code}")  # send verification code
                time.sleep(5)
                msg_type = classify_message(driver=web_driver, type="message")  # check if verification was successful
                if not msg_type == "success":
                    pause()
                    logging.info("Verification failed. Waiting for manual captcha solution...")
                    set_busy(False)
                    continue
                for i in range(10):     # if captcha was successful, skip down a few lines to avoid detection issues
                    send_command(web_driver=web_driver, command=f"Skipping lines: {i + 1}")
                    time.sleep(2)
                    set_busy(False)
            elif msg_type == "duplicate" or msg_type == "error":
                for i in range(5):
                    send_command(web_driver=web_driver, command=f"Skipping lines: {i + 1}")
                    time.sleep(2)
                set_busy(False)
                continue

            # Send proper command
            if MODE == "fishing":
                send_command(web_driver=web_driver, command="/fish")
            elif MODE == "farming":
                send_command(web_driver=web_driver, command="/farm")

            time.sleep(FISHING_COOLDOWN + random.random())

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
    global is_busy
    while is_busy:      # wait if something else is happening
        time.sleep(0.1) # wait a little
    is_busy = True      # when safe, lock sending

    if handle_chill_zone(web_driver=web_driver):
        return
    try:
        input_box = web_driver.find_element(By.XPATH, '//div[@role="textbox"]')
        input_box.send_keys(command)
        input_box.send_keys(Keys.ENTER)
        input_box.send_keys(Keys.ENTER)
        logging.info(f"Sent command: {command}")
    except Exception as e:
        logging.error(f"Failed to send command: {command}. Error: {e}")
    finally:
        is_busy = False # when done, unlock

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

def clear_bot_log(filepath="logs/bot.log"):
    try:
        with open(filepath, "w") as file:
            pass  # opening in write mode 'w' without writing anything empties the file
        print(f"✅ Cleared {filepath}.")
    except Exception as e:
        print(f"❌ Failed to clear {filepath}: {e}")

def handle_chill_zone(web_driver) -> bool:
    try:
        # Look for the modal by its label or unique button text
        chill_button = web_driver.find_element(By.XPATH, "//div[contains(text(), 'Enter the chill zone')]/ancestor::button")
        logging.info("Chill Zone detected. Clicking the button and cooling down...")
        chill_button.send_keys(Keys.ENTER)
        time.sleep(10)
        return True
    except NoSuchElementException:
        return False

def maybe_refresh(web_driver):
    global last_refresh_time
    if datetime.now() - last_refresh_time > REFRESH_INTERVAL:
        logging.info("Refreshing page to prevent slowdown...")
        web_driver.refresh()
        time.sleep(10)
        last_refresh_time = datetime.now()

def set_busy(state: bool):
    global is_busy
    is_busy = state

def can_send_command():
    return not is_busy
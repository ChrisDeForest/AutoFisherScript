import time
import threading
import logging
from datetime import datetime, timedelta

# Track if the main bot is paused externally
is_paused_ref = lambda: False
send_command_ref = None

# Define all boosts with priority (emerald > gold) and cooldowns (duration + 1min buffer)
BOOSTS = [
    {"name": "Auto30m", "command": "/buy Auto30m", "cooldown": 1860, "priority": "high"},
    {"name": "Fish20m", "command": "/buy Fish20m", "cooldown": 1260, "priority": "high"},
    {"name": "Treasure20m", "command": "/buy Treasure20m", "cooldown": 1260, "priority": "high"},
    {"name": "Auto10m", "command": "/buy Auto10m", "cooldown": 660, "priority": "low"},
    {"name": "Fish5m", "command": "/buy Fish5m", "cooldown": 360, "priority": "low"},
    {"name": "Treasure5m", "command": "/buy Treasure5m", "cooldown": 360, "priority": "low"},
]

# Track last used time for each boost
last_used = {boost["name"]: datetime.min for boost in BOOSTS}

def start_boost_scheduler(driver):
    def scheduler_loop():
        logging.info("Starting boost scheduler thread...")
        while True:
            if is_paused_ref():
                time.sleep(5)
                continue

            now = datetime.now()

            for boost in sorted(BOOSTS, key=lambda b: b["priority"], reverse=False):
                last_time = last_used[boost["name"]]
                if (now - last_time).total_seconds() >= boost["cooldown"]:
                    logging.info(f"Buying boost: {boost['name']}")
                    try:
                        if send_command_ref:
                            time.sleep(4)   # sleep for 4 seconds
                            send_command_ref(driver, boost["command"])
                        last_used[boost["name"]] = datetime.now()
                    except Exception as e:
                        logging.error(f"Failed to send boost command {boost['name']}: {e}")
            time.sleep(10)

    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()

# Setter functions to inject dependencies from fisher.py
def set_paused_getter(func):
    global is_paused_ref
    is_paused_ref = func

def set_command_sender(func):
    global send_command_ref
    send_command_ref = func

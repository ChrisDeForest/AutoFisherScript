from fisher import start_fishing
import logging

if __name__ == "__main__":
    logging.basicConfig(filename="logs/bot.log", level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logging.info("Launching AutoVirtualFisher...")
    start_fishing()

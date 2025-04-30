from fisher import start_fishing
from ollama_client import ensure_ollama_running
import logging

if __name__ == "__main__":
    logging.basicConfig(filename="logs/bot.log", level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    logging.info("Ensuring ollama is running...")
    ensure_ollama_running()

    logging.info("Launching AutoVirtualFisher...")
    start_fishing()

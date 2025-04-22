import os
import datetime

def ensure_dirs():
    os.makedirs("assets", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

# AutoFisherScript

Automates Virtual Fisher on Discord via browser interaction, simulating a real user. The bot uses Selenium and OCR to send /fish commands, detect captchas, and solve them automatically.

## 🚀 Features

- ✅ Auto-sends /fish every few seconds

- ✅ Detects and solves captchas using OCR (pytesseract)

- ✅ Verifies you're in the correct DM before acting

- ✅ Supports pause/resume with a global hotkey (Ctrl + Alt + P)

- ✅ Logs all actions and errors to a log file

## 📁 Project Structure

```
AutoFisherScript/
├── main.py             # Entry point
├── fisher.py           # Fishing loop logic
├── captcha.py          # OCR and captcha solving
├── utils.py            # Helpers (optional)
├── assets/             # Screenshots and captcha crops
├── logs/               # Bot logs
├── chrome_profile/     # Custom user data directory for Chrome
├── requirements.txt    # Python package requirements
└── README.md           # This file
```

## 🧱 Requirements

Install the required Python packages using:
```
pip install -r requirements.txt
```

Also install:

- Tesseract OCR: https://github.com/tesseract-ocr/tesseract

- ChromeDriver: Version must match your installed version of Chrome.

Ensure Tesseract is in your PATH, or set it manually in captcha.py:
```
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 🔧 Setup Instructions

1. Clone or copy the repo.

2. Download matching ChromeDriver for your Chrome version and point to it in fisher.py:
```
service = Service('D:/Tools/chromedriver.exe')
```
3. Update the Chrome user profile path:
```
options.add_argument(r"--user-data-dir=D:/Coding Projects/PycharmProjects/AutoFisherScript/chrome_profile")
```
4. Run the bot:
```
python main.py
```
5. Log into Discord manually in the opened Chrome window, then press Enter in the terminal.

> [!NOTE] 
> Don't forget to change any file paths mentioned above to the respectful paths on your machine

## ⏯️ Pause & Resume

Press ```Ctrl + Alt + P``` at any time in the terminal to pause or resume the bot.

When paused:

- The bot will wait without sending ```/fish```.

- You can activate boosts or perform manual actions.

# ⚡ Boost Auto-Buyer

The bot automatically buys boosts with cooldown padding (duration + 60 seconds):

|    Boost    |     Command      | Duration |   Priority   |
|:-----------:|:----------------:|:--------:|:------------:|
|   Auto30m   |   /buy Auto30m   |  30 min  | Emerald Fish |
|   Fish20m   |   /buy Fish20m   |  20 min  | Emerald Fish |
| Treasure20m | /buy Treasure20m |  20 min  | Emerald Fish |
|   Auto10m   |   /buy Auto10m   |  10 min  |  Gold Fish   |
|   Fish5m    |   /buy Fish5m    |  5 min   |  Gold Fish   |
| Treasure5m  | /buy Treasure5m  |  5 min   |  Gold Fish   |

- Boosts are prioritized by emerald > gold

- Boosts are staggered to avoid overlap

- Boost buying pauses if the bot is paused

## 💡 Notes

- This bot simulates user actions — it does not use the Discord API.

- Make sure you're on the correct DM with "Virtual Fisher" or the bot will not act.

- Captchas are solved based on visible text like /verify 3D6a or Code: 3D6a.

## 📌 Future Ideas

- Automate boost activation

- Auto-sell or open crates

- Track and log XP, gold, and rare catches

- GUI interface to control the bot

Made with ❤️ for fish.

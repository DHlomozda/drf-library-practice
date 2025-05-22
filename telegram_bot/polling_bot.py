import os
import time
import django
import requests
from dotenv import load_dotenv

from telegram_bot.utils import handle_start_command
from telegram_bot.telegram import TELEGRAM_TOKEN, send_telegram_message


load_dotenv()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "library_service.settings"
)

django.setup()

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"


def get_updates(offset=None):
    response = requests.get(
        BASE_URL + "getUpdates",
        params={"timeout": 100, "offset": offset}
    )
    return response.json() if response.ok else None


def process_update(update):
    message = update.get("message", {})
    text = message.get("text", "")
    chat_id = message["chat"]["id"]
    telegram_user_id = message["from"]["id"]

    if text.startswith("/start"):
        parts = text.split()
        if len(parts) < 2:
            send_telegram_message(
                "Будь ласка, введіть команду у форматі "
                "/start your_email",
                chat_id)
            return

        email = parts[1].strip()

        handle_start_command(chat_id, email, telegram_user_id)


def main():
    print("Polling bot is running...")
    offset = None

    while True:
        updates = get_updates(offset)
        if updates and updates.get("ok"):
            for update in updates["result"]:
                offset = update["update_id"] + 1
                process_update(update)
        time.sleep(1)


if __name__ == "__main__":
    main()

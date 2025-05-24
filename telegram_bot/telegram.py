import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GROUP_INVITE_LINK = os.getenv("TELEGRAM_GROUP_INVITE_LINK")


def send_telegram_message(text: str, chat_id: str = CHAT_ID):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    })

    if not response.ok:
        raise Exception(f"Failed to send message: {response.text}")

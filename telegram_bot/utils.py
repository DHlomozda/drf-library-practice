import re
from django.contrib.auth import get_user_model
from .telegram import send_telegram_message, GROUP_INVITE_LINK

User = get_user_model()

def handle_start_command(chat_id: int, email: str, telegram_user_id: int):
    if not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        send_telegram_message("Невірний формат email.", chat_id)
        return

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        send_telegram_message("Користувача з такою email-адресою не знайдено.", chat_id)
        return

    existing_user = User.objects.filter(telegram_id=telegram_user_id).exclude(email=email).first()
    if existing_user:
        send_telegram_message("❌ Цей Telegram вже прив’язано до іншого акаунту.", chat_id)
        return

    user.telegram_id = telegram_user_id
    user.save()

    send_telegram_message(
        f"Привіт, {user.first_name}! Ось посилання на приватний чат: {GROUP_INVITE_LINK}",
        chat_id
    )

# import re
# from django.contrib.auth import get_user_model
# from .telegram import send_telegram_message, GROUP_INVITE_LINK
#
# User = get_user_model()
#
#
# def handle_start_command(payload: dict) -> None:
#     print("=== НОВЕ ПОВІДОМЛЕННЯ ВІД TELEGRAM ===")
#     print(payload)
#     message = payload.get("message", {})
#     chat_id = message.get("chat", {}).get("id")
#     text = message.get("text", "").strip()
#
#     if not text.startswith("/start"):
#         return
#
#     parts = text.split()
#
#     if len(parts) == 1:
#         # Користувач написав просто /start без email
#         send_telegram_message(
#             "👋 Вітаю! Будь ласка, введіть свою електронну пошту у форматі:\n"
#             "/start your@email.com",
#             chat_id
#         )
#         return
#
#     if len(parts) == 2:
#         email = parts[1].strip()
#
#         if not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
#             send_telegram_message("❌ Невірний формат email. Спробуйте ще раз.", chat_id)
#             return
#
#         try:
#             user = User.objects.get(email=email)
#             send_telegram_message(
#                 f"👋 Привіт, {user.username or email}!\n"
#                 f"Ось посилання на групу сповіщень: {GROUP_INVITE_LINK}",
#                 chat_id
#             )
#         except User.DoesNotExist:
#             send_telegram_message("❌ Користувача з таким email не знайдено.", chat_id)
#         return
#
#     # Якщо команда має неправильний формат (більше 2 частин)
#     send_telegram_message(
#         "❌ Невірний формат команди. Введіть у вигляді:\n"
#         "/start your@email.com",
#         chat_id
#     )
#
#
# def handle_telegram_update(payload: dict) -> None:
#     message = payload.get("message", {})
#     text = message.get("text", "")
#
#     if text.startswith("/start"):
#         handle_start_command(payload)

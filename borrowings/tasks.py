from celery import shared_task
from django.utils import timezone
from borrowings.models import Borrowing
from telegram_bot.telegram import send_telegram_message


@shared_task
def check_overdue_borrowings():
    now = timezone.now()
    overdue = Borrowing.objects.filter(
        expected_return_date__lt=now,
        actual_return_date__isnull=True
    ).select_related("user", "book")

    if not overdue.exists():
        send_telegram_message("No borrowings overdue today!")
        return

    for obj in overdue:
        message = (
            f"📚 <b>Overdue Borrowing</b>\n"
            f"👤 User: {obj.user.email}\n"
            f"📖 Book: {obj.book.title}\n"
            f"📅 Expected Return: "
            f"{obj.expected_return_date.strftime('%Y-%m-%d %H:%M')}"
        )
        send_telegram_message(message)

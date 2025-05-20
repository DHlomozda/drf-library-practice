from celery import shared_task
from django.utils import timezone
from borrowings.models import Borrowing


@shared_task
def check_overdue_borrowings():
    now = timezone.now()
    overdue = Borrowing.objects.filter(
        expected_return_date__lt=now,
        actual_return_date__isnull=True
    ).select_related("user", "book")

    if not overdue.exists():
        print("No borrowings overdue today!")
        return

    for obj in overdue:
        print(
            f"📚 Overdue!\n"
            f"Email: {obj.user.email}\n"
            f"Book: {obj.book.title}\n"
            f"Expected: {obj.expected_return_date}"
        )

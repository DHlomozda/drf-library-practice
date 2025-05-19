from django.db import models
from django.conf import settings
from decimal import Decimal


class Borrowing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_id = models.CharField(
        max_length=255
    )
    session_url = models.URLField(
        max_length=500
    )
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PAYMENT
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Payment {self.status} for borrowing {self.borrowing.id}"

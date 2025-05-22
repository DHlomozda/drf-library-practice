from django.db import models
from django.core.exceptions import ValidationError


class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=CoverType.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        if self.inventory < 0:
            raise ValidationError(
                {"inventory": "Inventory must be a positive number."}
            )

        if self.daily_fee <= 0:
            raise ValidationError(
                {"daily_fee": "Daily fee must be a positive number."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author}"

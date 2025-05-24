from rest_framework import serializers
from borrowings.models import Borrowing
from books.serializers import BookReadSerializer
from payment_service.serializers import PaymentSerializer


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookReadSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )

    def validate_expected_return_date(self, value):
        from django.utils.timezone import now
        if value <= now():
            raise serializers.ValidationError(
                "Expected return date must be in the future."
            )
        return value

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory <= 0:
            raise serializers.ValidationError({
                'book': "Sorry, the book is currently"
                        " unavailable for borrowing"
            })
        return attrs

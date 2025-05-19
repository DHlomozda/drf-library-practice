from rest_framework import serializers
from borrowings.models import Borrowing
from books.serializers import BookReadSerializer


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookReadSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )

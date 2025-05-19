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


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["book", "expected_return_date"]

    def validate(self, data):
        book = data.get("book")
        if book.inventory <= 0:
            raise serializers.ValidationError("Sorry, this book is currently out of stock")
        return data

    def create(self, validated_data):
        book = validated_data.get("book")
        book.inventory -= 1
        book.save()

        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError("You must log in to proceed")

        borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing

from rest_framework import serializers
from django.core.exceptions import ValidationError
from books.models import Book


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")

    def validate(self, data):
        inventory = data.get("inventory")
        daily_fee = data.get("daily_fee")
        title = data.get("title")
        author = data.get("author")

        if inventory is not None and inventory <= 0:
            raise serializers.ValidationError(
                {"inventory": "Inventory must be a positive number."}
            )

        if daily_fee is not None and daily_fee <= 0:
            raise serializers.ValidationError(
                {"daily_fee": "Daily fee must be a positive number."}
            )

        if title and author:
            if Book.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    {
                        "title":
                            "Book with this title and author already exists."
                    }
                )

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class BookReadSerializer(serializers.ModelSerializer):
    daily_fee = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")

    def get_daily_fee(self, obj):
        return f"${obj.daily_fee:.2f}"

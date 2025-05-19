from rest_framework import serializers

from books.models import Book


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title", "author", "cover", "inventory", "daily_fee")


class BookReadSerializer(serializers.ModelSerializer):
    daily_fee = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee", "daily_fee")

    def get_daily_fee(self, obj):
        return f"${obj.daily_fee}"

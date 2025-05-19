from rest_framework import viewsets

from books.models import Book
from books.serializers import BookReadSerializer, BookCreateSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BookReadSerializer
        return BookCreateSerializer

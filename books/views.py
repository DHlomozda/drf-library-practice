from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.schema_descriptions import (
    book_list_schema,
    book_retrieve_schema,
    book_create_schema,
    book_update_schema,
    book_partial_update_schema,
    book_destroy_schema
)
from books.serializers import BookReadSerializer, BookCreateSerializer
from books.utils.mixins import ActionMixin


class BookViewSet(ActionMixin):
    queryset = Book.objects.all()
    action_serializers = {
        "list": BookReadSerializer,
        "retrieve": BookReadSerializer,
        "create": BookCreateSerializer,
        "update": BookCreateSerializer,
        "partial_update": BookCreateSerializer,
    }
    permission_classes = [IsAdminOrReadOnly]

    @book_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @book_retrieve_schema
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @book_create_schema
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @book_update_schema
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @book_partial_update_schema
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @book_destroy_schema
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

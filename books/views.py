from books.models import Book
from books.permissions import IsAdminOrReadOnly
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

from rest_framework import viewsets
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer


class BorrowingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingReadSerializer
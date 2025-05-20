from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timezone

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)
from payment_service.stripe_service import create_stripe_checkout_session


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        
        days_rented = (borrowing.expected_return_date - borrowing.borrow_date).days
        if days_rented <= 0:
            days_rented = 1
            
        amount = borrowing.book.daily_fee * days_rented
        
        create_stripe_checkout_session(
            borrowing=borrowing,
            amount=amount,
            payment_type="PAYMENT",
            request=self.request
        )

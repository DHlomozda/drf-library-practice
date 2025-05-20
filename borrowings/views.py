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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")
        if user.is_staff:
            queryset = queryset.filter(user_id=user_id) if user_id else queryset
        if is_active and is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)
        return queryset if user.is_staff else queryset.filter(user=user)

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

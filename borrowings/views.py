from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)
from payment_service.stripe_service import create_stripe_checkout_session


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = Borrowing.objects.select_related("book", "user")

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

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        
        if borrowing.actual_return_date:
            return Response(
                {"error": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        borrowing.actual_return_date = datetime.now(timezone.utc)
        
        book = borrowing.book
        book.inventory += 1
        book.save()
        
        borrowing.save()
        
        return Response(
            {"message": "Book has been successfully returned."},
            status=status.HTTP_200_OK
        )

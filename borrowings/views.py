from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone
from django.conf import settings

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)
from borrowings.schema_descriptions import (
    borrowing_list_schema,
    borrowing_retrieve_schema,
    borrowing_create_schema,
    borrowing_update_schema,
    borrowing_partial_update_schema,
    borrowing_destroy_schema,
    borrowing_return_schema,
)
from payment_service.stripe_service import create_stripe_checkout_session
from telegram_bot.telegram import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @borrowing_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @borrowing_retrieve_schema
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @borrowing_create_schema
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @borrowing_update_schema
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @borrowing_partial_update_schema
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @borrowing_destroy_schema
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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
        
        book = borrowing.book
        book.inventory -= 1
        book.save()
        
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

        message = (
            f"📚 <b>New Borrowing Created</b>\n"
            f"👤 User: {borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title}\n"
            f"📅 Borrow Date: {borrowing.borrow_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"📅 Expected Return: {borrowing.expected_return_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"💰 Amount: ${amount:.2f}"
        )
        send_telegram_message(message)

    @borrowing_return_schema
    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        
        if borrowing.actual_return_date:
            return Response(
                {"error": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        borrowing.actual_return_date = datetime.now(timezone.utc)
        
        if borrowing.actual_return_date > borrowing.expected_return_date:
            days_overdue = (borrowing.actual_return_date - borrowing.expected_return_date).days
            fine_amount = days_overdue * borrowing.book.daily_fee * settings.FINE_MULTIPLIER
            
            create_stripe_checkout_session(
                borrowing=borrowing,
                amount=fine_amount,
                payment_type="FINE",
                request=request
            )
        
        book = borrowing.book
        book.inventory += 1
        book.save()
        
        borrowing.save()
        
        return Response(
            {"message": "Book has been successfully returned."},
            status=status.HTTP_200_OK
        )

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone
from django.conf import settings
from django.db.models import Q

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
from borrowings.permissions import IsOwnerOrAdmin
from payment_service.stripe_service import create_stripe_checkout_session
from payment_service.models import Payment
from telegram_bot.telegram import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    @borrowing_list_schema
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().list(request, *args, **kwargs)

    @borrowing_retrieve_schema
    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = Borrowing.objects.select_related("book", "user")

        if user.is_staff:
            queryset = queryset.filter(user_id=user_id) if user_id else queryset

        if is_active and is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset if user.is_staff else queryset.filter(user=user)

    @borrowing_create_schema
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        pending_payments = Payment.objects.filter(
            borrowing__user=request.user,
            status__in=[Payment.Status.PENDING, Payment.Status.EXPIRED]
        )
        
        if pending_payments.exists():
            return Response(
                {
                    "detail": "You have pending payments that need to "
                              "be completed before borrowing new books."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
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

    @action(
        detail=True,
        methods=["post"],
        url_path="return",
        permission_classes=[IsOwnerOrAdmin],
    )
    @borrowing_return_schema
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"detail": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        if borrowing.actual_return_date > borrowing.expected_return_date:
            days_overdue = (
                borrowing.actual_return_date - borrowing.expected_return_date
            ).days
            fine_amount = borrowing.book.daily_fee * 2 * days_overdue

            try:
                payment = create_stripe_checkout_session(
                    borrowing=borrowing,
                    amount=fine_amount,
                    payment_type=Payment.Type.FINE,
                    request=request,
                )
                return Response(
                    {
                        "detail": "Book returned successfully. A fine has been issued for late return.",
                        "fine_payment_id": payment.id,
                        "fine_amount": fine_amount,
                        "checkout_url": payment.session_url,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"detail": f"Error creating fine payment: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"detail": "Book returned successfully."},
            status=status.HTTP_200_OK,
        )

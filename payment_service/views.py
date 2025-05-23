import stripe
from datetime import datetime, timezone
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram_bot.telegram import send_telegram_message

from borrowings.models import Borrowing
from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer
from payment_service.permissions import IsAdminOrReadOnly
from payment_service.stripe_service import (
    create_stripe_checkout_session,
    StripeSessionError
)

from payment_service.schema_descriptions import (
    payment_list_schema,
    payment_retrieve_schema,
    start_payment_schema,
    payment_success_schema,
    payment_cancel_schema,
    stripe_webhook_schema,
    renew_payment_schema,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "id"]
    search_fields = ["status", "id"]

    @payment_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @payment_retrieve_schema
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)


class StartPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @start_payment_schema
    def post(self, request, borrowing_id):
        borrowing = get_object_or_404(Borrowing, id=borrowing_id)

        if borrowing.user != request.user and not request.user.is_staff:
            return Response({"detail": "Not allowed."}, status=403)

        existing_payment = Payment.objects.filter(
            borrowing=borrowing,
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT
        ).first()

        if existing_payment:
            return Response({
                "payment_id": existing_payment.id,
                "checkout_url": existing_payment.session_url
            }, status=201)

        end_date = borrowing.actual_return_date or datetime.now(timezone.utc)

        days_rented = (end_date - borrowing.borrow_date).days
        if days_rented <= 0:
            days_rented = 1

        amount = borrowing.book.daily_fee * days_rented

        try:
            payment = create_stripe_checkout_session(
                borrowing=borrowing,
                amount=amount,
                payment_type=Payment.Type.PAYMENT,
                request=request
            )

            return Response({
                "payment_id": payment.id,
                "checkout_url": payment.session_url
            }, status=201)
        except StripeSessionError as e:
            return Response({"error": str(e)}, status=400)


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    @payment_success_schema
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        if (
                payment.borrowing.user != request.user
                and not request.user.is_staff
        ):
            return Response({"detail": "Not allowed."}, status=403)

        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.payment_status == 'paid':
                payment.status = Payment.Status.PAID
                payment.save()

                if (
                        payment.type == Payment.Type.PAYMENT
                        and not payment.borrowing.actual_return_date
                ):
                    borrowing = payment.borrowing
                    borrowing.actual_return_date = datetime.now(timezone.utc)
                    borrowing.save()
                    book = borrowing.book
                    book.inventory += 1
                    book.save()

                message = (
                    f"Payment completed successfully!\n"
                    f"Borrowing ID: #{payment.borrowing.id}\n"
                    f"Amount: ${payment.money_to_pay}\n"
                    f"Type: {payment.type}\n"
                    f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                send_telegram_message(message)

                return Response({
                    "status": "success",
                    "message": "Payment completed successfully"
                })
            else:
                return Response({
                    "status": "pending",
                    "message": "Payment is still pending"
                })
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)


class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    @payment_cancel_schema
    def get(self, request):
        return Response({
            "status": "cancelled",
            "message": "Payment was cancelled. You can try again later."
                       " The session will be available for 24 hours."
        })


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = []

    @stripe_webhook_schema
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            session_id = session.get('id')

            try:
                payment = Payment.objects.get(session_id=session_id)
                payment.status = Payment.Status.PAID
                payment.save()
            except Payment.DoesNotExist:
                return HttpResponse(status=404)

        return HttpResponse(status=200)


class RenewPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @renew_payment_schema
    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        if (
                payment.borrowing.user != request.user
                and not request.user.is_staff
        ):
            return Response({"detail": "Not allowed."}, status=403)

        if payment.status != Payment.Status.EXPIRED:
            return Response(
                {"detail": "Only expired payments can be renewed."},
                status=400
            )

        try:
            new_payment = create_stripe_checkout_session(
                borrowing=payment.borrowing,
                amount=payment.money_to_pay,
                payment_type=payment.type,
                request=request
            )

            payment.status = Payment.Status.EXPIRED
            payment.save()

            return Response({
                "payment_id": new_payment.id,
                "checkout_url": new_payment.session_url
            }, status=201)
        except StripeSessionError as e:
            return Response({"error": str(e)}, status=400)

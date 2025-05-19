import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowings.models import Borrowing
from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer
from payment_service.permissions import IsOwnerOrAdmin
from payment_service.stripe_service import create_stripe_checkout_session


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)


class StartPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, borrowing_id):
        borrowing = get_object_or_404(Borrowing, id=borrowing_id)

        if borrowing.user != request.user and not request.user.is_staff:
            return Response({"detail": "Not allowed."}, status=403)

        amount = borrowing.book.daily_fee * 5
        payment = create_stripe_checkout_session(
            borrowing=borrowing,
            amount=amount,
            payment_type=Payment.Type.PAYMENT,
        )

        return Response({
            "payment_id": payment.id,
            "checkout_url": payment.session_url
        })


class PaymentCancelView(APIView):
    def get(self, request):
        return Response({"detail": "The payment was forfeited"})


# TO-DO
# @method_decorator(csrf_exempt, name='dispatch')
# class StripeWebhookView(APIView):
#     def post(self, request):
#         payload = request.body
#         sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#         endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
#
#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, endpoint_secret
#             )
#         except ValueError:
#             return HttpResponse(status=400)
#         except stripe.error.SignatureVerificationError:
#             return HttpResponse(status=400)
#
#         if event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             session_id = session.get('id')
#
#             try:
#                 payment = Payment.objects.get(session_id=session_id)
#                 payment.status = Payment.Status.PAID
#                 payment.save()
#             except Payment.DoesNotExist:
#                 return HttpResponse(status=404)
#
#         return HttpResponse(status=200)

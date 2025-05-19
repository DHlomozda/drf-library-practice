from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payment_service.views import PaymentViewSet, PaymentCancelView
from payment_service.views import StartPaymentView


router = DefaultRouter()

router.register(
    r"",
    PaymentViewSet,
    basename="payment"
)

urlpatterns = [
    path(
        "start/<int:borrowing_id>/",
        StartPaymentView.as_view(),
        name="start-payment"
    ),

    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),

    path("", include(router.urls)),

    # TO-D0
    # path(
    #     'payments/webhook/',
    #     StripeWebhookView.as_view(),
    #     name='stripe-webhook'
    #  )
]

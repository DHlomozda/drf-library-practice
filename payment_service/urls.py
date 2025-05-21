from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payment_service.views import (
    PaymentViewSet,
    PaymentCancelView,
    StartPaymentView,
    PaymentSuccessView,
    StripeWebhookView,
    RenewPaymentView,
)


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
    
    path("success/<int:payment_id>/", PaymentSuccessView.as_view(), name="payment-success"),
    
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),

    path("renew/<int:payment_id>/", RenewPaymentView.as_view(), name="renew-payment"),

    path("", include(router.urls)),

]

from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from payment_service.serializers import PaymentSerializer


payment_list_schema = extend_schema(
    summary="Get list of payments",
    description=(
        "Admins can view all payments. "
        "Regular users see only their own payments."
    ),
    responses={200: PaymentSerializer(many=True)},
)

payment_retrieve_schema = extend_schema(
    summary="Retrieve a payment",
    description="Get detailed information about a specific payment.",
    responses={200: PaymentSerializer},
)

start_payment_schema = extend_schema(
    summary="Start a payment session",
    description=(
        "Create a Stripe checkout session for a borrowing.\n\n"
        "- If a pending session already exists, returns it.\n"
        "- Otherwise creates a new Stripe session.\n"
        "- Only the borrower or an admin can initiate this."
    ),
    responses={
        201: OpenApiTypes.OBJECT
    }
)

payment_success_schema = extend_schema(
    summary="Confirm payment success",
    description=(
        "Check Stripe payment status.\n"
        "- If paid: update status to PAID.\n"
        "- If pending: keep as pending.\n"
        "- Restricted to borrower or admin."
    ),
    responses={200: OpenApiTypes.OBJECT}
)

payment_cancel_schema = extend_schema(
    summary="Payment cancelled",
    description="Informs user that the payment was cancelled.",
    responses={200: OpenApiTypes.OBJECT}
)

stripe_webhook_schema = extend_schema(
    summary="Stripe webhook handler",
    description="Receives webhook events from Stripe and updates payment status.",
    responses={200: None}
)

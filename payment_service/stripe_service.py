import stripe
from django.conf import settings
from payment_service.models import Payment
from decimal import Decimal


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_checkout_session(
        borrowing,
        amount: Decimal,
        payment_type: str
) -> Payment:

    user_email = borrowing.user.email if borrowing.user else None
    if not user_email:
        raise ValueError("User email is required for creating payment session")

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Borrowing #{borrowing.id} - {payment_type}',
                },
                'unit_amount': int(round(amount * 100)),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/api/payments/',
        cancel_url='http://localhost:8000/api/payments/cancel/',
        customer_email=user_email,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=amount,
        type=payment_type
    )
    return payment


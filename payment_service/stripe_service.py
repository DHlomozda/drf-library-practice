import stripe
from django.conf import settings
from django.urls import reverse
from payment_service.models import Payment
from decimal import Decimal
from typing import Optional
from django.core.exceptions import ValidationError
from datetime import datetime, timezone, timedelta


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeSessionError(Exception):
    """Custom exception for Stripe session creation errors"""
    pass


def create_stripe_checkout_session(
        borrowing,
        amount: Decimal,
        payment_type: str,
        request
) -> Payment:
    """
    Create a Stripe checkout session for payment.
    
    Args:
        borrowing: The borrowing instance
        amount: The amount to charge
        payment_type: Type of payment (PAYMENT or FINE)
        request: The request object for building absolute URLs
        
    Returns:
        Payment: Created payment instance
        
    Raises:
        StripeSessionError: If there's an error creating the Stripe session
        ValidationError: If input validation fails
    """
    if amount <= 0:
        raise ValidationError("Amount must be positive")

    if payment_type not in [Payment.Type.PAYMENT, Payment.Type.FINE]:
        raise ValidationError("Invalid payment type")

    user_email = borrowing.user.email if borrowing.user else None
    if not user_email:
        raise ValidationError("User email is required for creating payment session")

    # Create payment first to get its ID
    try:
        payment = Payment.objects.create(
            borrowing=borrowing,
            session_id="",  # Will be updated after session creation
            session_url="",  # Will be updated after session creation
            money_to_pay=amount,
            type=payment_type
        )
    except Exception as e:
        raise StripeSessionError(f"Failed to create payment record: {str(e)}")

    # Build success and cancel URLs
    success_url = request.build_absolute_uri(
        reverse('payment-success', kwargs={'payment_id': payment.id})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payment-cancel')
    )

    try:
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
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user_email,
            expires_at=int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()),
        )

        # Update payment with session details
        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

    except stripe.error.StripeError as e:
        payment.delete()
        raise StripeSessionError(f"Failed to create Stripe session: {str(e)}")
    except Exception as e:
        payment.delete()
        raise StripeSessionError(f"Unexpected error creating Stripe session: {str(e)}")

    return payment


import stripe
from django.conf import settings
from payment_service.models import Payment
from telegram_bot.telegram import send_telegram_message

stripe.api_key = settings.STRIPE_SECRET_KEY

def check_expired_sessions():
    """
    Check for expired Stripe sessions and update payment statuses.
    This task should be scheduled to run every minute.
    """
    pending_payments = Payment.objects.filter(status=Payment.Status.PENDING)
    
    for payment in pending_payments:
        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            
            if session.status == 'expired':
                payment.status = Payment.Status.EXPIRED
                payment.save()
                
                message = (
                    f"Payment session for borrowing #{payment.borrowing.id} has expired.\n"
                    f"Amount: ${payment.money_to_pay}\n"
                    f"Type: {payment.type}\n"
                    f"You can create a new payment session to complete the payment."
                )
                send_telegram_message(message)
                
        except stripe.error.StripeError as e:
            print(f"Error checking session {payment.session_id}: {str(e)}")
            continue 

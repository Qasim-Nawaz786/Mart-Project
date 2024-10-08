# import httpx
import stripe
from app.settings import STRIPE_API_KEY  # Assuming this is set in your environment

# Initialize the Stripe API key
stripe.api_key = STRIPE_API_KEY
print("Stripe API key", stripe.api_key)

async def create_payment_intent(amount: int, currency: str, customer_email: str) -> dict:
    try:
        # Create a PaymentIntent with Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            receipt_email=customer_email
        )
        return payment_intent
    except stripe.error.StripeError as e:
        return {"error": str(e)}

async def retrieve_payment_intent(payment_intent_id: str) -> dict:
    try:
        # Retrieve an existing PaymentIntent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except stripe.error.StripeError as e:
        return {"error": str(e)}

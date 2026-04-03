import os
import stripe
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from dotenv import load_dotenv

from db.schemas.stripe import CheckoutRequest

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

app = FastAPI(title="Stripe Payments Demo")

@app.post("/create-checkout-session")
def create_checkout_session(data: CheckoutRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": data.currency,
                        "product_data": {"name": data.product_name},
                        "unit_amount": data.amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=data.success_url,
            cancel_url=data.cancel_url,
        )
        return {"checkout_url": session.url}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        # handle_successful_payment(session)

    elif event_type == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        # handle_failed_payment(intent)

    # Πάντα επιστρέφουμε 200 — το Stripe ξαναστέλνει αν δεν λάβει 200
    return {"received": True}
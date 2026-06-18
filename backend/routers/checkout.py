import os
from datetime import datetime, timedelta, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from db.database import get_db
from db.models.movies import Movie
from db.models.users import User
from db.models.rentals import Rental
from db.models.purchases import Purchase
from db.models.payments import Payment
from db.schemas.checkout import CheckoutCreate, CheckoutResponse
from utils.auth import get_current_user

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Διάρκεια ενοικίασης (επιλογή χρήστη: 2 ημέρες)
RENTAL_DAYS = 2

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("/", response_model=CheckoutResponse)
def create_checkout(
    data: CheckoutCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    movie = db.query(Movie).filter(Movie.id == data.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    if data.kind == "rental":
        amount = movie.rental_price
        label = f"Ενοικίαση: {movie.title}"
    else:  # purchase
        amount = movie.purchase_price
        label = f"Αγορά: {movie.title}"

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": label},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            success_url=f"{FRONTEND_URL}/?checkout=success",
            cancel_url=f"{FRONTEND_URL}/?checkout=cancel",
            client_reference_id=str(user.id),
            # Όλα όσα χρειάζεται το webhook για να γράψει την εγγραφή
            metadata={
                "user_id": str(user.id),
                "movie_id": str(movie.id),
                "kind": data.kind,
            },
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CheckoutResponse(checkout_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        _fulfill_checkout(event["data"]["object"], db)

    # Πάντα 200 — αλλιώς το Stripe ξαναστέλνει το event
    return {"received": True}


def _fulfill_checkout(session: dict, db: Session) -> None:
    """Γράφει Payment + Rental/Purchase. Idempotent: το unique
    stripe_checkout_session_id εμποδίζει διπλή εγγραφή σε retries."""
    session_id = session["id"]

    # Έχει ήδη επεξεργαστεί αυτό το session;
    if db.query(Payment).filter(
        Payment.stripe_checkout_session_id == session_id
    ).first():
        return

    metadata = session.get("metadata") or {}
    user_id = metadata.get("user_id")
    movie_id = metadata.get("movie_id")
    kind = metadata.get("kind")
    if not (user_id and movie_id and kind):
        return

    amount = session.get("amount_total") or 0

    # Δημιουργία της εγγραφής αγοράς/ενοικίασης
    if kind == "rental":
        now = datetime.now(timezone.utc)
        record = Rental(
            user_id=user_id,
            movie_id=movie_id,
            start_date=now,
            end_date=now + timedelta(days=RENTAL_DAYS),
        )
    else:  # purchase
        record = Purchase(
            user_id=user_id,
            movie_id=movie_id,
            amount_paid=amount,
        )

    db.add(record)
    db.flush()  # για να πάρουμε το record.id πριν το commit

    payment = Payment(
        user_id=user_id,
        stripe_checkout_session_id=session_id,
        stripe_payment_intent_id=session.get("payment_intent") or session_id,
        amount=amount,
        currency=session.get("currency") or "eur",
        status="paid",
        payment_type=kind,
        referrence_id=record.id,
    )
    db.add(payment)
    db.commit()

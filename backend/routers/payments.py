import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.models.payments import Payment
from db.database import get_db
from db.schemas.payment import PaymentResponse


router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=list[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db)
):
    return db.query(Payment).all()

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404, detail=f"Payment with id {payment_id} not found")

    return payment

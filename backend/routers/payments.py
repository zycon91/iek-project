import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.models.users import User
from utils.auth import require_admin
from db.schemas.pagination import Page
from db.models.payments import Payment
from db.database import get_db
from db.schemas.payment import PaymentResponse


router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=Page[PaymentResponse])
def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    total = db.query(Payment).count()

    items = db.query(Payment).offset(skip).limit(limit).all()

    return Page[PaymentResponse](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404, detail=f"Payment with id {payment_id} not found")

    return payment

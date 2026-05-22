import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.models.purchases import Purchase
from db.database import get_db
from db.schemas.purchase import PurchaseResponse


router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.get("/", response_model=list[PurchaseResponse])
def get_purchases(
    db: Session = Depends(get_db)
):
    return db.query(Purchase).all()

@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(
    purchase_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    purchase = db.query(Purchase).filter(
        purchase_id = Purchase.id
    ).first()

    if not purchase:
        raise HTTPException(
            status_code=404, detail=f"Purchase with id {purchase_id} not found")
    
    return purchase
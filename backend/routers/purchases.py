import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.models.users import User
from utils.auth import require_admin
from db.schemas.pagination import Page
from db.models.purchases import Purchase
from db.database import get_db
from db.schemas.purchase import PurchaseResponse


router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.get("/", response_model=Page[PurchaseResponse])
def get_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    total = db.query(Purchase).count()

    items = db.query(Purchase).offset(skip).limit(limit).all()

    return Page[PurchaseResponse](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )

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
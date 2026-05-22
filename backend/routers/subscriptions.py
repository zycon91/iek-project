import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.schemas.pagination import Page
from db.models.subscriptions import Subscription
from db.database import get_db
from db.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/", response_model=Page[SubscriptionResponse])
def get_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Subscription).count()

    items = db.query(Subscription).offset(skip).limit(limit).all()

    return Page[SubscriptionResponse](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail=f"Subscription with ID {subscription_id}not found.")
    
    return subscription

@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Subscription).filter(
        Subscription.user_id == data.user_id,
        Subscription.is_active == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has an active subscription.")
    
    subscription = Subscription(**data.model_dump())
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription

@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: uuid.UUID,
    data: SubscriptionUpdate,
    db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)

    db.commit()
    db.refresh(subscription)
    return subscription

@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(subscription_id: uuid.UUID, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found.")

    db.delete(subscription)
    db.commit()

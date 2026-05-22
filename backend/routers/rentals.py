import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.schemas.pagination import Page
from db.models.rentals import Rental
from db.database import get_db
from db.schemas.rental import RentalCreate, RentalResponse, RentalUpdate

router = APIRouter(prefix="/rentals", tags=["rentals"])

@router.get("/", response_model=Page[RentalResponse])
def get_rentals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    total = db.query(Rental).count()

    items = db.query(Rental).offset(skip).limit(limit).all()

    return Page[RentalResponse](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )

@router.get("/{rental_id}", response_model=RentalResponse)
def get_rental(
    rental_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    rental =  db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail=f"Rental with ID {rental_id}not found.")

    return rental

@router.post("/", response_model=RentalResponse, status_code=202)
def create_rental(
    data: RentalCreate,
    db: Session = Depends(get_db)
):
    rental = Rental(**data.model_dump())
    db.add(rental)
    db.commit()
    db.refresh(rental)
    
    return rental

@router.patch("/", response_model=RentalResponse)
def update_rental(
    rental_id: uuid.UUID,
    data: RentalUpdate,
    db: Session = Depends(get_db)
):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental with ID {rental_id}not found.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rental, field, value)

    db.commit()
    db.refresh(rental)
    return rental

@router.delete("/{rental_id}", status_code=204)
def delete_rental(
    rental_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental with ID {rental_id}not found.")
    
    db.delete(rental)
    db.commit()

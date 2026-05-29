import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.schemas.pagination import Page
from db.database import get_db
from db.models.users import User
from db.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=Page[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None),
    sort_by: str = Query("username"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))
    
    sort_columns = {
        "username": User.username,
        "fullname": User.fullname,
        "email": User.email
    }

    column = sort_columns.get(sort_by, User.username)
    query = query.order_by(column.desc() if order == "desc" else column.asc())

    total = query.count()

    items = query.offset(skip).limit(limit).all()

    return Page[UserResponse](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with User ID: {user_id} not found.")
    return user

@router.post("/", response_model=UserResponse, status_code = 201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_email = db.query(User).filter(
        User.email == user_data.email).first()
    existing_username = db.query(User).filter(
        User.username == user_data.username).first()
    
    if existing_email:
        raise HTTPException(
            status_code=400, detail="Email already in use")
    if existing_username:
        raise HTTPException(
            status_code=400, detail="Username already in use")
    
    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
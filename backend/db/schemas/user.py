import uuid
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str
    fullname: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    fullname: str | None = None

class UserResponse(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
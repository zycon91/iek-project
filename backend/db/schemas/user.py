import uuid
from typing import Literal
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
    role: str

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]

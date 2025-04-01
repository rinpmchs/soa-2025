from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# class UserCreate(BaseModel):
#     login: str
#     email: EmailStr
#     password: str

class UserCreate(BaseModel):
    login: str = Field(..., min_length=4, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=30)


class UserResponse(BaseModel):
    id: int
    login: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[str]
    phone_number: Optional[str]
    email: Optional[EmailStr]

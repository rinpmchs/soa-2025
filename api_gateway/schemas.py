from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PostStats(BaseModel):
    views: int
    likes: int
    comments: int


class DailyStat(BaseModel):
    date: str  # YYYY-MM-DD
    count: int


class DailyStats(BaseModel):
    stats: List[DailyStat]


class TopItem(BaseModel):
    id: str
    count: int


class TopPosts(BaseModel):
    posts: List[TopItem]


class TopUsers(BaseModel):
    users: List[TopItem]


class MetricEnum(str, Enum):
    views = "views"
    likes = "likes"
    comments = "comments"


class LikeRequest(BaseModel):
    post_id: int


class CommentRequest(BaseModel):
    post_id: int
    text: str


class PostCreate(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: List[str] = []


class PostUpdate(PostCreate):
    pass  # можно будет расширить позже


class PostResponse(PostCreate):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str


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

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, UserUpdate
from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user


router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Handles user registration."""

    existing_user = db.query(User).filter((User.login == user_data.login) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Login or email already exists")

    hashed_password = hash_password(user_data.password)

    new_user = User(
        login=user_data.login,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# @router.post("/login", response_model=TokenResponse)
# def login(user_data: LoginRequest, db: Session = Depends(get_db)):
#     """Authenticates user and returns JWT token."""
#     user = db.query(User).filter(User.login == user_data.login).first()
#
#     if not user or not verify_password(user_data.password, user.password_hash):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
#
#     # Generate JWT token
#     access_token = create_access_token({"sub": user.login})
#     return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 Login: Authenticate user and return JWT"""
    user = db.query(User).filter(User.login == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token({"sub": user.login})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Returns current user profile (protected route)."""
    return current_user


@router.put("/update", response_model=UserResponse)
def update_user_profile(
        updated_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Updates user profile fields except login & password."""

    if updated_data.email:
        existing_user = db.query(User).filter(User.email == updated_data.email, User.id != current_user.id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")

    for field, value in updated_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user

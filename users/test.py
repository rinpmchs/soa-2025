import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming FastAPI app is initialized in main.py
from database import get_db
from models import User
from auth import create_access_token
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DATABASE_URL
from schemas import UserCreate
from auth import verify_password


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def test_user():
    return {"email": "test@example.com", "password": "securepassword"}


@pytest.fixture
def create_test_user(test_user):
    db = next(override_get_db())
    hashed_password = verify_password(test_user["password"], test_user["password"])
    user = User(email=test_user["email"], hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_register_user(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 201
    assert response.json()["email"] == test_user["email"]


def test_register_existing_user(create_test_user, test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 400


def test_login_user(create_test_user, test_user):
    response = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(create_test_user, test_user):
    response = client.post("/login", data={"username": test_user["email"], "password": "wrongpassword"})
    assert response.status_code == 401


def test_login_non_existent_user():
    response = client.post("/login", data={"username": "fake@example.com", "password": "password"})
    assert response.status_code == 401


def test_token_generation(create_test_user, test_user):
    token = create_access_token(data={"sub": test_user["email"]})
    assert isinstance(token, str)

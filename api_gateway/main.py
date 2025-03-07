from fastapi import FastAPI, HTTPException, Depends
import httpx
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8000/users")

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifies JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI(title="API Gateway", description="Proxy for User Service")


@app.post("/api/users/register")
async def register_user(user_data: dict):
    """Proxy for user registration"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/register", json=user_data)
        return response.json()


@app.post("/api/users/authenticate")
async def authenticate_user(credentials: dict):
    """Proxy for user login"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/login", json=credentials)
        return response.json()


@app.put("/api/users/profile")
async def update_profile(profile_data: dict, user=Depends(verify_token)):
    """Proxy for updating user profile (Requires authentication)"""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{USER_SERVICE_URL}/update",
            json=profile_data,
            headers={"Authorization": f"Bearer {user['sub']}"}
        )
        return response.json()


@app.get("/api/users/profile")
async def get_profile(user=Depends(verify_token)):
    """Proxy for getting user profile (Requires authentication)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{USER_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {user['sub']}"}
        )
        return response.json()

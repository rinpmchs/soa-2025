from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
import httpx
import config
from schemas import UserCreate, UserUpdate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


async def make_request(method, endpoint, json=None, headers=None):
    """Send requests to the Users Service."""
    url = f"{config.USER_SERVICE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())


@router.post("/register")
async def register_user(user: UserCreate):
    return await make_request("POST", "/register", json=user.dict())



@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    data = {"login": form_data.username, "password": form_data.password}
    return await make_request("POST", "/login_json", json=data)


@router.get("/me")
async def get_profile(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    return await make_request("GET", "/me", headers=headers)


@router.put("/me")
async def update_profile(user_update: UserUpdate, token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    return await make_request("PUT", "/update", json=user_update.dict(), headers=headers)

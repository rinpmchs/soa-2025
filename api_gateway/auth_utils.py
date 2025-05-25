from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.users_service_url}/users/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return {
                "id": user_data["id"],
                "token": token
            }
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth failed: {str(e)}")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


# async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
#     headers = {"Authorization": f"Bearer {token}"}
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(f"{settings.users_service_url}/users/me", headers=headers)
#         if response.status_code == 200:
#             user_data = response.json()
#             return user_data["id"]
#         raise HTTPException(status_code=401, detail="Invalid token")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Auth failed: {str(e)}")
#

async def verify_token(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.users_service_url}/users/me", headers=headers)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
import pytest
from httpx import AsyncClient
from users.main import app


@pytest.mark.asyncio
async def test_register_user_creates_record():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/users/register", json={"login": "rina", "email": "rina@gmail.com", "password": "rina1234"})
        assert resp.status_code == 200
        # assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_returns_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/users/register", json={"login": "rina", "email": "rina@gmail.com", "password": "rina1234"})
        resp = await ac.post("/users/login", data={"username": "tester2", "password": "pass"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_profile_returns_user_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        reg = await ac.post("/users/register", json={"login": "rina", "email": "rina@gmail.com", "password": "rina1234"})
        token = reg.json()["access_token"]
        resp = await ac.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["login"] == "rina"


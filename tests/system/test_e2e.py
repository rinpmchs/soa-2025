import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_create_post_and_check_stats():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        user = await ac.post("/users/register", json={"login": "tatiana", "email": "anima@x.com", "password": "tatanima"})
        token = user.json()["access_token"]
        post = await ac.post("/posts/create", json={"title": "E2E", "description": "the post for testing on the system level"}, headers={"Authorization": f"Bearer {token}"})
        stats = await ac.get("/stats/user", headers={"Authorization": f"Bearer {token}"})
        assert stats.status_code == 200
        assert stats.json()["posts_count"] >= 1


@pytest.mark.asyncio
async def test_post_liked_and_stat_updated():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        user = await ac.post("/users/register", json={"login": "liker", "email": "liker@x.com", "password": "pw"})
        token = user.json()["access_token"]
        post = await ac.post("/posts/create", json={"title": "Like", "description": "Me"}, headers={"Authorization": f"Bearer {token}"})
        post_id = post.json()["id"]
        await ac.post(f"/posts/{post_id}/like", headers={"Authorization": f"Bearer {token}"})
        stats = await ac.get(f"/stats/post/{post_id}", headers={"Authorization": f"Bearer {token}"})
        assert stats.status_code == 200
        assert stats.json()["likes_count"] == 1


@pytest.mark.asyncio
async def test_post_commented_and_visible_in_feed():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        user = await ac.post("/users/register", json={"login": "comm", "email": "comm@x.com", "password": "pw"})
        token = user.json()["access_token"]
        post = await ac.post("/posts/create", json={"title": "C", "description": "D"}, headers={"Authorization": f"Bearer {token}"})
        post_id = post.json()["id"]
        await ac.post(f"/posts/{post_id}/comment", json={"text": "Nice!"}, headers={"Authorization": f"Bearer {token}"})
        feed = await ac.get("/feed", headers={"Authorization": f"Bearer {token}"})
        comments = feed.json()["posts"][0]["comments"]
        assert any(c["text"] == "Nice!" for c in comments)

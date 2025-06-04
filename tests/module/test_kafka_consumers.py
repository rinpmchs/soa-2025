import pytest
import asyncio
from posts.repositories import get_post_by_id, get_post_likes_count


@pytest.mark.asyncio
async def test_post_created_event_saves_to_db(kafka_env, db_session):
    kafka_env.producer.produce("post_created", key="id", value='{"id": "1", "title": "X", "creator_id": "u1"}')
    kafka_env.producer.flush()
    await asyncio.sleep(2)
    post = await get_post_by_id(db_session, "1")
    assert post is not None
    assert post.title == "X"


@pytest.mark.asyncio
async def test_like_event_increments_count(kafka_env, db_session):
    kafka_env.producer.produce("post_liked", key="like", value='{"post_id": "1"}')
    kafka_env.producer.flush()
    await asyncio.sleep(2)
    stats = await get_post_likes_count(db_session, "1")
    assert stats.likes == 1

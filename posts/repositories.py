from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models import Post, Like, Comment
from typing import Optional


async def get_post_by_id(session: AsyncSession, post_id: str) -> Optional[Post]:
    result = await session.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def get_post_likes_count(session: AsyncSession, post_id: str) -> int:
    result = await session.execute(
        select(func.count(Like.id)).where(Like.post_id == post_id)
    )
    return result.scalar_one()


async def get_post_comments(session: AsyncSession, post_id: str) -> list[Optional[Comment]]:
    result = await session.execute(
        select(Comment).where(Comment.post_id == post_id)
    )
    return result.scalars().all()


async def get_user_posts_count(session: AsyncSession, user_id: str) -> int:
    result = await session.execute(
        select(func.count(Post.id)).where(Post.creator_id == user_id)
    )
    return result.scalar_one()

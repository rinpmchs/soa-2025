import pytest


@pytest.mark.asyncio
async def test_get_user_post_stats_returns_correct(grpc_stats_stub, mock_post_repo):
    mock_post_repo.get_posts_count.return_value = 5
    stats = await grpc_stats_stub.GetUserStats(user_id="abc")
    assert stats.posts_count == 5


@pytest.mark.asyncio
async def test_get_post_likes_returns_count(grpc_stats_stub, mock_like_repo):
    mock_like_repo.get_likes_count.return_value = 3
    result = await grpc_stats_stub.GetPostLikes(post_id="xyz")
    assert result.likes_count == 3


@pytest.mark.asyncio
async def test_top_users_by_likes(grpc_stats_stub, mock_user_repo):
    mock_user_repo.get_top_users_by_likes.return_value = ["user1", "user2"]
    result = await grpc_stats_stub.GetTopUsers()
    assert result.user_ids == ["user1", "user2"]

import pytest
from uuid import uuid4
# from posts.models import Post
from posts.repositories import get_post_by_id


@pytest.mark.asyncio
async def test_create_post_saves_to_db(grpc_post_stub, db_session):
    user_id = str(uuid4())
    response = await grpc_post_stub.CreatePost(title="first post", description="hello, this is the first post", creator_id=user_id)
    post = await get_post_by_id(db_session, response.post.id)
    assert post is not None
    assert post.title == "first post"


@pytest.mark.asyncio
async def test_update_post_changes_data(grpc_post_stub, db_session):
    user_id = str(uuid4())
    create_resp = await grpc_post_stub.CreatePost(title="post",
                                                  description="this post is just to check the creation and updateability", creator_id=user_id)
    post_id = create_resp.post.id
    await grpc_post_stub.UpdatePost(id=post_id, title="update", description="this post has been updated", requester_id=user_id)
    post = await get_post_by_id(db_session, post_id)
    assert post.title == "update"
    assert post.description == "this post has been updated"


@pytest.mark.asyncio
async def test_delete_post_removes_from_db(grpc_post_stub, db_session):
    user_id = str(uuid4())
    create_resp = await grpc_post_stub.CreatePost(title="bye", description="this post will be deleted", creator_id=user_id)
    await grpc_post_stub.DeletePost(id=create_resp.post.id, requester_id=user_id)
    post = await get_post_by_id(db_session, create_resp.post.id)
    assert post is None

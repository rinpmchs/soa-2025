from fastapi import APIRouter, HTTPException, Depends, Query, Body
from proto import posts_pb2, posts_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
from typing import List
from schemas import PostCreate, PostUpdate, PostResponse, ViewPostResponse
from auth_utils import get_current_user
from config import kafka_producer
import json


router = APIRouter()

channel = grpc.insecure_channel("posts_service:50052")
stub = posts_pb2_grpc.PostServiceStub(channel)


@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, user=Depends(get_current_user)):
    request = posts_pb2.LikePostRequest(
        post_id=post_id,
        client_id=str(user['id'])
    )
    stub.LikePost(request)
    event = {
        "event_type": "like",
        "post_id": post_id
    }
    kafka_producer.produce(
        topic="post_events",
        key=post_id,
        value=json.dumps(event).encode('utf-8')
    )
    kafka_producer.flush()
    return {"message": "post liked"}


@router.post("/posts/{post_id}/comment")
async def comment_post(
    post_id: str,
    body: dict = Body(...),
    user=Depends(get_current_user)
):
    text = body.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="missing comment text")

    request = posts_pb2.CommentPostRequest(
        post_id=post_id,
        client_id=str(user['id']),
        text=text
    )
    stub.CommentPost(request)

    event = {
        "event_type": "comment",
        "post_id": post_id,
    }
    kafka_producer.produce(
        topic="post_events",
        key=post_id,
        value=json.dumps(event).encode('utf-8')
    )
    kafka_producer.flush()
    return {"message": "comment added"}


@router.post("/posts/{post_id}/view")
async def view_post(post_id: str, user=Depends(get_current_user)):
    request = posts_pb2.ViewPostRequest(
        post_id=post_id,
        client_id=str(user['id'])
    )
    stub.ViewPost(request)

    event = {
        "event_type": "view",
        "post_id": post_id
    }
    kafka_producer.produce(
        topic="post_events",
        key=post_id,
        value=json.dumps(event).encode('utf-8')
    )
    kafka_producer.flush()
    return ViewPostResponse(
        id=grpc_response.post.id,
        title=grpc_response.post.title,
        description=grpc_response.post.description,
        creator_id=grpc_response.post.creator_id,
        created_at=grpc_response.post.created_at.ToDatetime(),
        updated_at=grpc_response.post.updated_at.ToDatetime(),
        is_private=grpc_response.post.is_private,
        tags=grpc_response.post.tags
    )
    return {"message": "post viewed"}


@router.post("/create", response_model=PostResponse)
async def create_post(post: PostCreate, user=Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.CreatePostRequest(
            title=post.title,
            description=post.description,
            creator_id=str(user["id"]),
            is_private=post.is_private,
            tags=post.tags
        )
        grpc_response = stub.CreatePost(grpc_request)
        return PostResponse(
            id=grpc_response.post.id,
            title=grpc_response.post.title,
            description=grpc_response.post.description,
            creator_id=grpc_response.post.creator_id,
            created_at=grpc_response.post.created_at.ToDatetime(),
            updated_at=grpc_response.post.updated_at.ToDatetime(),
            is_private=grpc_response.post.is_private,
            tags=grpc_response.post.tags
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: str, user=Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.GetPostRequest(
            id=post_id,
            requester_id=str(user["id"])
        )
        grpc_response = stub.GetPost(grpc_request)
        return PostResponse(
            id=grpc_response.post.id,
            title=grpc_response.post.title,
            description=grpc_response.post.description,
            creator_id=grpc_response.post.creator_id,
            created_at=grpc_response.post.created_at.ToDatetime(),
            updated_at=grpc_response.post.updated_at.ToDatetime(),
            is_private=grpc_response.post.is_private,
            tags=grpc_response.post.tags
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=404, detail=f"gRPC error: {e.details()}")


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post: PostUpdate, user=Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.UpdatePostRequest(
            id=post_id,
            requester_id=str(user["id"]),
            title=post.title,
            description=post.description,
            is_private=post.is_private,
            tags=post.tags
        )
        grpc_response = stub.UpdatePost(grpc_request)
        return PostResponse(
            id=grpc_response.post.id,
            title=grpc_response.post.title,
            description=grpc_response.post.description,
            creator_id=grpc_response.post.creator_id,
            created_at=grpc_response.post.created_at.ToDatetime(),
            updated_at=grpc_response.post.updated_at.ToDatetime(),
            is_private=grpc_response.post.is_private,
            tags=grpc_response.post.tags
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.delete("/{post_id}")
async def delete_post(post_id: str, user=Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.DeletePostRequest(
            id=post_id,
            requester_id=str(user["id"])
        )
        grpc_response = stub.DeletePost(grpc_request)
        return {"success": grpc_response.success}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.get("/list_posts", response_model=List[PostResponse])
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user=Depends(get_current_user)
):
    try:
        grpc_request = posts_pb2.ListPostsRequest(
            page=page,
            page_size=page_size,
            requester_id=str(user["id"])
        )
        grpc_response = stub.ListPosts(grpc_request)
        return [
            PostResponse(
                id=str(post.id),
                title=post.title,
                description=post.description,
                creator_id=post.creator_id,
                created_at=post.created_at.ToDatetime(),
                updated_at=post.updated_at.ToDatetime(),
                is_private=post.is_private,
                tags=post.tags
            )
            for post in grpc_response.posts
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.get("/list_posts", response_model=List[PostResponse])
async def list_posts(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        user=Depends(get_current_user)
):
    try:
        creator_id = str(user["id"])
        grpc_request = posts_pb2.ListPostsRequest(
            page=page,
            page_size=page_size,
            creator_id=creator_id
        )
        grpc_response = stub.ListPosts(grpc_request)
        return [
            PostResponse(
                id=post.id,
                title=post.title,
                description=post.description,
                creator_id=post.creator_id,
                created_at=post.created_at.ToDatetime(),
                updated_at=post.updated_at.ToDatetime(),
                is_private=post.is_private,
                tags=post.tags
            )
            for post in grpc_response.posts
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

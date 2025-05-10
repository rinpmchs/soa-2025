from fastapi import APIRouter, HTTPException, Depends, Query
from proto import posts_pb2, posts_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import grpc
from typing import List
from schemas import PostCreate, PostUpdate, PostResponse
from auth_utils import get_current_user

router = APIRouter()

channel = grpc.insecure_channel("posts_service:50052")
stub = posts_pb2_grpc.PostServiceStub(channel)


@router.post("/create", response_model=PostResponse)
async def create_post(post: PostCreate, user_id: str = Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.CreatePostRequest(
            title=post.title,
            description=post.description,
            creator_id=user_id,
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
def get_post(post_id: str, user_id: str = Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.GetPostRequest(
            id=post_id,
            requester_id=user_id
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
async def update_post(post_id: str, post: PostUpdate, user_id: str = Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.UpdatePostRequest(
            id=post_id,
            requester_id=user_id,
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
async def delete_post(post_id: str, user_id: str = Depends(get_current_user)):
    try:
        grpc_request = posts_pb2.DeletePostRequest(
            id=post_id,
            requester_id=user_id
        )
        grpc_response = stub.DeletePost(grpc_request)
        return {"success": grpc_response.success}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")


@router.get("/list_posts", response_model=List[PostResponse])
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: str = Depends(get_current_user)
):
    try:
        grpc_request = posts_pb2.ListPostsRequest(
            page=page,
            page_size=page_size,
            requester_id=user_id
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


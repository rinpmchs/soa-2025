import os
from enum import Enum
import grpc
from fastapi import APIRouter, HTTPException, Query
from typing import List
from schemas import PostStats, DailyStats, DailyStat, TopPosts, MetricEnum, TopItem, TopUsers
from proto import stats_pb2, stats_pb2_grpc

router = APIRouter(prefix="/stats", tags=["statistics"])

# Environment variable: e.g. "statistics_service:50052"
STATISTICS_SERVICE_URL = os.getenv("STATISTICS_SERVICE_URL", "statistics_service:50052")
channel = grpc.insecure_channel(STATISTICS_SERVICE_URL)
stub = stats_pb2_grpc.StatisticsStub(channel)


@router.get("/posts/{post_id}", response_model=PostStats)
def get_post_stats(post_id: str):
    try:
        req = stats_pb2.PostStatsRequest(post_id=post_id)
        res = stub.GetPostStats(req)
        return PostStats(views=res.views, likes=res.likes, comments=res.comments)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or str(e))


@router.get("/posts/{post_id}/views", response_model=DailyStats)
def get_post_views_daily(post_id: str):
    try:
        req = stats_pb2.PostStatsRequest(post_id=post_id)
        res = stub.GetPostViewsDaily(req)
        return DailyStats(stats=[DailyStat(date=d.date, count=d.count) for d in res.stats])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or str(e))


@router.get("/posts/{post_id}/likes", response_model=DailyStats)
def get_post_likes_daily(post_id: str):
    try:
        req = stats_pb2.PostStatsRequest(post_id=post_id)
        res = stub.GetPostLikesDaily(req)
        return DailyStats(stats=[DailyStat(date=d.date, count=d.count) for d in res.stats])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or str(e))


@router.get("/posts/{post_id}/comments", response_model=DailyStats)
def get_post_comments_daily(post_id: str):
    try:
        req = stats_pb2.PostStatsRequest(post_id=post_id)
        res = stub.GetPostCommentsDaily(req)
        return DailyStats(stats=[DailyStat(date=d.date, count=d.count) for d in res.stats])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or str(e))


@router.get("/top/posts", response_model=TopPosts)
def get_top_posts(
    metric: MetricEnum = Query(..., description="Metric to sort by: views, likes, or comments"),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        # Map string to enum value
        metric_enum = stats_pb2.TopRequest.Metric.Value(metric.name.upper())
        req = stats_pb2.TopRequest(metric=metric_enum, limit=limit)
        res = stub.GetTopPosts(req)
        return TopPosts(posts=[TopItem(id=i.id, count=i.count) for i in res.posts])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or str(e))

@router.get("/top/users", response_model=TopUsers)
def get_top_users(
    metric: MetricEnum = Query(..., description="Metric to sort by: views, likes, or comments"),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        metric_enum = stats_pb2.TopRequest.Metric.Value(metric.name.upper())
        req = stats_pb2.TopRequest(metric=metric_enum, limit=limit)
        res = stub.GetTopUsers(req)
        return TopUsers(users=[TopItem(id=i.id, count=i.count) for i in res.users])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or str(e))

from proto import posts_pb2, posts_pb2_grpc
from database import SessionLocal
from models import Post, Like, Comment
from google.protobuf.timestamp_pb2 import Timestamp
from sqlalchemy.exc import NoResultFound
from uuid import UUID
import grpc
from confluent_kafka import Producer
import json
import os
from dotenv import load_dotenv


load_dotenv()
producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})


def send_to_kafka(topic: str, event: dict):
    producer.produce(topic, json.dumps(event).encode("utf-8"))
    producer.flush()


class PostService(posts_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        session = SessionLocal()
        db_post = Post(
            title=request.title,
            description=request.description,
            creator_id=request.creator_id,
            is_private=request.is_private,
            tags=list(request.tags)
        )
        session.add(db_post)
        session.commit()
        session.refresh(db_post)

        created_at = Timestamp()
        created_at.FromDatetime(db_post.created_at)
        updated_at = Timestamp()
        updated_at.FromDatetime(db_post.updated_at)

        return posts_pb2.CreatePostResponse(
            post=posts_pb2.Post(
                id=str(db_post.id),
                title=db_post.title,
                description=db_post.description,
                creator_id=db_post.creator_id,
                created_at=created_at,
                updated_at=updated_at,
                is_private=db_post.is_private,
                tags=db_post.tags
            )
        )

    def GetPost(self, request, context):
        session = SessionLocal()

        try:
            post_id = UUID(request.id)
            post = session.query(Post).filter(Post.id == post_id).one()

            if post.is_private and post.creator_id != request.requester_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "This post is private.")

            created_at = Timestamp()
            updated_at = Timestamp()
            created_at.FromDatetime(post.created_at)
            updated_at.FromDatetime(post.updated_at)

            return posts_pb2.GetPostResponse(
                post=posts_pb2.Post(
                    id=str(post.id),
                    title=post.title,
                    description=post.description,
                    creator_id=post.creator_id,
                    created_at=created_at,
                    updated_at=updated_at,
                    is_private=post.is_private,
                    tags=post.tags
                )
            )

        except NoResultFound:
            context.abort(grpc.StatusCode.NOT_FOUND, "Post not found.")
        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
        finally:
            session.close()

    def DeletePost(self, request, context):
        session = SessionLocal()
        try:
            post_id = UUID(request.id)
            post = session.query(Post).filter(Post.id == post_id).one_or_none()

            if post is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

            if post.creator_id != request.requester_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "You are not the owner of this post")

            session.delete(post)
            session.commit()

            return posts_pb2.DeletePostResponse(success=True)

        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
        finally:
            session.close()

    def UpdatePost(self, request, context):
        session = SessionLocal()
        try:
            post_id = UUID(request.id)
            post = session.query(Post).filter(Post.id == post_id).one_or_none()
            if post is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

            if post.creator_id != request.requester_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED,
                              "You are not the creator of this post and cannot update it.")

            post.title = request.title
            post.description = request.description
            post.is_private = request.is_private
            post.tags = list(request.tags)

            session.commit()
            session.refresh(post)

            created_at = Timestamp()
            updated_at = Timestamp()
            created_at.FromDatetime(post.created_at)
            updated_at.FromDatetime(post.updated_at)

            return posts_pb2.UpdatePostResponse(
                post=posts_pb2.Post(
                    id=str(post.id),
                    title=post.title,
                    description=post.description,
                    creator_id=post.creator_id,
                    created_at=created_at,
                    updated_at=updated_at,
                    is_private=post.is_private,
                    tags=post.tags
                )
            )

        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
        finally:
            session.close()

    def ListPosts(self, request, context):
        session = SessionLocal()
        try:
            posts_query = session.query(Post)

            posts_query = posts_query.filter(
                (Post.is_private == False) | (str(Post.creator_id) == request.requester_id)
            )

            offset = (request.page - 1) * request.page_size
            posts = posts_query.offset(offset).limit(request.page_size).all()
            total = posts_query.count()
            # posts = posts_query.offset(request.offset).limit(request.limit).all()

            response = posts_pb2.ListPostsResponse(total=total)
            for post in posts:
                created_at = Timestamp()
                updated_at = Timestamp()
                created_at.FromDatetime(post.created_at)
                updated_at.FromDatetime(post.updated_at)

                response.posts.append(posts_pb2.Post(
                    id=str(post.id),
                    title=post.title,
                    description=post.description,
                    creator_id=post.creator_id,
                    created_at=created_at,
                    updated_at=updated_at,
                    is_private=post.is_private,
                    tags=post.tags
                ))

            return response

        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
        finally:
            session.close()

    def LikePost(self, request, context):
        db = SessionLocal()
        try:
            like = Like(
                post_id=request.post_id,
                client_id=request.client_id
            )
            db.add(like)
            db.commit()

            ts = Timestamp()
            ts.GetCurrentTime()
            event = {
                "event_type": "like",
                "post_id": request.post_id,
                "client_id": request.client_id,
                "timestamp": ts.ToJsonString()
            }
            send_to_kafka("post_liked", event)

            return posts_pb2.LikePostResponse()

        except Exception as e:
            db.rollback()
            context.set_details(f"Error liking post: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return posts_pb2.LikePostResponse()

        finally:
            db.close()

    def CommentPost(self, request, context):
        db = SessionLocal()
        try:
            comment = Comment(
                post_id=request.post_id,
                client_id=request.client_id,
                text=request.text
            )
            db.add(comment)
            db.commit()

            ts = Timestamp()
            ts.GetCurrentTime()
            event = {
                "event_type": "comment",
                "post_id": request.post_id,
                "client_id": request.client_id,
                "text": request.text,
                "timestamp": ts.ToJsonString()
            }
            send_to_kafka("post_commented", event)

            return posts_pb2.CommentPostResponse()

        except Exception as e:
            db.rollback()
            context.set_details(f"Error commenting post: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return posts_pb2.CommentPostResponse()

        finally:
            db.close()

    def GetPostComments(self, request, context):
        db = SessionLocal()
        try:
            page = max(1, request.page)
            limit = min(request.limit or 10, 100)
            offset = (page - 1) * limit

            comments_query = db.query(Comment).filter_by(post_id=request.post_id) \
                .order_by(Comment.created_at.desc()) \
                .offset(offset).limit(limit).all()

            response = posts_pb2.GetPostCommentsResponse()

            for c in comments_query:
                response.comments.add(
                    client_id=c.client_id,
                    text=c.text,
                    created_at=c.created_at.isoformat()
                )

            return response

        except Exception as e:
            context.set_details(f"Error getting comments: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return posts_pb2.GetPostCommentsResponse()

        finally:
            db.close()

    def ViewPost(self, request, context):
        try:
            ts = Timestamp()
            ts.GetCurrentTime()

            event = {
                "event_type": "view",
                "post_id": request.post_id,
                "client_id": request.client_id,
                "timestamp": ts.ToJsonString()
            }
            send_to_kafka("post_viewed", event)

            return posts_pb2.ViewPostResponse()

        except Exception as e:
            context.set_details(f"Error viewing post: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return posts_pb2.ViewPostResponse()

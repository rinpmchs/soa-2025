from proto import posts_pb2, posts_pb2_grpc
from database import SessionLocal
from models import Post
from google.protobuf.timestamp_pb2 import Timestamp
from sqlalchemy.exc import NoResultFound
from uuid import UUID
import grpc


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
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "You are not the owner of this post")

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

            # фильтруем приватные посты, которые НЕ принадлежат текущему пользователю
            posts_query = posts_query.filter(
                (Post.is_private == False) | (Post.creator_id == request.requester_id)
            )

            posts = posts_query.offset(request.offset).limit(request.limit).all()

            response = posts_pb2.ListPostsResponse()
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

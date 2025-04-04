import grpc
from concurrent import futures
from proto import posts_pb2_grpc
from post_service import PostService
from models import Base
from database import engine

Base.metadata.create_all(bind=engine)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port('[::]:50052')
    print("PostService gRPC running on port 50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    serve()

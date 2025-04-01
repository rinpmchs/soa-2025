import grpc
from proto import posts_pb2, posts_pb2_grpc


def create_post(stub):
    request = posts_pb2.CreatePostRequest(
        title="Тестовый пост",
        description="Для проверки метода GetPost",
        creator_id="test-user-id",
        is_private=False,
        tags=["grpc", "get"]
    )
    try:
        response = stub.CreatePost(request)
        print("post created damn yayy:", response.post.id)
        print(response)
        return response.post.id
    except grpc.RpcError as e:
        print("gRPC error:")
        print(f"{e.code()}: {e.details()}")


def get_post(stub, post_id):
    request = posts_pb2.GetPostRequest(
        id=post_id,
        requester_id="test-user-id"
    )
    try:
        response = stub.GetPost(request)
        print("success! we got post:")
        print(response.post)
    except grpc.RpcError as e:
        print("gRPC error:")
        print(f"{e.code()}: {e.details()}")


def delete_post(stub, post_id):
    request = posts_pb2.DeletePostRequest(
        id=post_id,
        requester_id="test-user-id"
    )
    try:
        response = stub.DeletePost(request)
        print("slayy!! post deleted:", response.success)
    except grpc.RpcError as e:
        print("gRPC error:")
        print(f"{e.code()}: {e.details()}")


def run():
    channel = grpc.insecure_channel("localhost:50052")
    stub = posts_pb2_grpc.PostServiceStub(channel)

    post_id = create_post(stub)
    get_post(stub, post_id)
    delete_post(stub, post_id)


if __name__ == "__main__":
    run()

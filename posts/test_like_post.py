import grpc
from proto import posts_pb2, posts_pb2_grpc


def like_post(stub):
    request = posts_pb2.LikePostRequest(
        post_id="be238a69-1a11-46c4-aa4d-5732b3384056",
        client_id="4"
    )
    try:
        response = stub.LikePost(request)
        print("post liked damn yayy")
        print(response)
        return
    except grpc.RpcError as e:
        print("gRPC error (post like):")
        print(f"{e.code()}: {e.details()}")


def comment_post(stub):
    request = posts_pb2.CommentPostRequest(
        post_id="be238a69-1a11-46c4-aa4d-5732b3384056",
        client_id="4",
        text="отличный пост!"
    )
    try:
        response = stub.CommentPost(request)
        print("post commented damnnn")
        print(response)
        return
    except grpc.RpcError as e:
        print("gRPC error (post like):")
        print(f"{e.code()}: {e.details()}")


def run():
    channel = grpc.insecure_channel("localhost:50052")
    stub = posts_pb2_grpc.PostServiceStub(channel)

    like_post(stub)
    comment_post(stub)


if __name__ == "__main__":
    run()

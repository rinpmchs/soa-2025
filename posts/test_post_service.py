import grpc
from proto import posts_pb2, posts_pb2_grpc


def create_post(stub):
    request = posts_pb2.CreatePostRequest(
        title="Первый пост",
        description="этот пост мы будем получать и удалять потом",
        creator_id="test-user-id",
        is_private=False,
        tags=["grpc", "new", "test", "get", "delete"]
    )
    try:
        response = stub.CreatePost(request)
        print("post created damn yayy:", response.post.id)
        print(response)
        return response.post.id
    except grpc.RpcError as e:
        print("gRPC error (post create first):")
        print(f"{e.code()}: {e.details()}")


def create_post_sasha(stub):
    request = posts_pb2.CreatePostRequest(
        title="Пост про Сашу",
        description="Саша пошел пить кофе 10 минут назад",
        creator_id="test-user-id",
        is_private=False,
        tags=["grpc", "new", "get"]
    )
    try:
        response = stub.CreatePost(request)
        print("post created damn yayy:", response.post.id)
        print(response)
        return response.post.id
    except grpc.RpcError as e:
        print("gRPC error (post create):")
        print(f"{e.code()}: {e.details()}")


def create_post_dasha(stub):
    request = posts_pb2.CreatePostRequest(
        title="Пост про Дашу",
        description="Даша полетела в Париж на две недели",
        creator_id="dasha-user-id",
        is_private=False,
        tags=["grpc", "new", "get"]
    )
    try:
        response = stub.CreatePost(request)
        print("post created damn yayy:", response.post.id)
        print(response)
        return response.post.id
    except grpc.RpcError as e:
        print("gRPC error (post create):")
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
        print("gRPC error (post get):")
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
        print("gRPC error (post delete):")
        print(f"{e.code()}: {e.details()}")


def update_post(stub, post_id):
    request = posts_pb2.UpdatePostRequest(
        id=post_id,
        requester_id="test-user-id",
        title="Обновлённый пост про Сашу",
        description="Саша вернулся довольный",
        is_private=True,
        tags=["updated", "private", "new"]
    )
    try:
        response = stub.UpdatePost(request)
        print("post updated !:")
        print(response.post)
    except grpc.RpcError as e:
        print("grpc error (post update):")
        print(f"{e.code()}: {e.details()}")


def update_post_not_creator(stub, post_id):
    request = posts_pb2.UpdatePostRequest(
        id=post_id,
        requester_id="test-user-id",
        title="Обновлённый пост про Дашу",
        description="Даша попала в авиакатастрофу",
        is_private=False,
        tags=["updated", "private", "new"]
    )
    try:
        response = stub.UpdatePost(request)
        print("post updated !:")
        print(response.post)
    except grpc.RpcError as e:
        print("grpc error (post update by wrong user - not creator):")
        print(f"{e.code()}: {e.details()}")


def list_posts(stub):
    request = posts_pb2.ListPostsRequest(
        page_size=10,
        page=1,
        requester_id="test-user-id"
    )
    try:
        ids = []
        response = stub.ListPosts(request)
        print(f"number of posts: {len(response.posts)}")
        for post in response.posts:
            ids.append(post.id)
            print("-", post, "\n")
        print(ids)
    except grpc.RpcError as e:
        print("grpc error (posts list):")
        print(f"{e.code()}: {e.details()}")


def list_posts_not_creator(stub):
    request = posts_pb2.ListPostsRequest(
        page_size=10,
        page=1,
        requester_id="another-user-id"
    )
    try:
        response = stub.ListPosts(request)
        print(f"number of posts: {len(response.posts)}")
        for post in response.posts:
            print("-", post, "\n")
    except grpc.RpcError as e:
        print("grpc error (posts list (without private ones)):")
        print(f"{e.code()}: {e.details()}")


def run():
    channel = grpc.insecure_channel("localhost:50052")
    stub = posts_pb2_grpc.PostServiceStub(channel)

    post_id = create_post(stub)
    post_id_sasha = create_post_sasha(stub)
    post_id_dasha = create_post_dasha(stub)
    get_post(stub, post_id)
    # add trying to get private post
    update_post_not_creator(stub, post_id_dasha)
    update_post(stub, post_id_sasha)
    list_posts(stub)
    delete_post(stub, post_id)
    list_posts_not_creator(stub)

    # ids = []
    # for id in ids:
    #     delete_post(stub, id)

if __name__ == "__main__":
    run()

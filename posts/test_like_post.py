import grpc
from posts.proto import posts_pb2, posts_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = posts_pb2_grpc.PostServiceStub(channel)

request = posts_pb2.LikePostRequest(
    post_id="some-post-id",
    client_id="some-client-id"
)

response = stub.LikePost(request)
print(response)

import grpc
from concurrent import futures
import config
from database import init_database
from kafka_consumer import thread  # starts on import
from proto import stats_pb2_grpc as grpc_pb
from stats_service import StatisticsServicer


def serve():
    init_database()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_pb.add_StatisticsServicer_to_server(StatisticsServicer(), server)
    server.add_insecure_port(f"[::]:{config.GRPC_PORT}")
    server.start()
    print(f"gRPC server running on port {config.GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

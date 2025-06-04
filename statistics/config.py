import os

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 9000))
CLICKHOUSE_DB   = os.getenv("CLICKHOUSE_DB",   "stats")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPICS = {
    "views":    os.getenv("KAFKA_TOPIC_VIEWS",    "post_views"),
    "likes":    os.getenv("KAFKA_TOPIC_LIKES",    "post_likes"),
    "comments": os.getenv("KAFKA_TOPIC_COMMENTS", "post_comments"),
}

GRPC_PORT = os.getenv("GRPC_PORT", "50052")
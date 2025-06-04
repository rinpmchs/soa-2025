from clickhouse_driver import Client
from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_DB

admin_client = Client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT
)

db = Client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    database=CLICKHOUSE_DB
)


def init_database():
    admin_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")

    db.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_date Date,
        post_id    String,
        user_id    String,
        event_type String
    ) ENGINE = MergeTree()
    PARTITION BY event_date
    ORDER BY (event_date, post_id, user_id, event_type)
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS daily_aggregates (
        date   Date,
        id     String,
        metric String,
        count  UInt64
    ) ENGINE = AggregatingMergeTree()
    PARTITION BY date
    ORDER BY (date, id, metric)
    """)

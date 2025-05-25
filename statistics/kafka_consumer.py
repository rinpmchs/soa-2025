import json
import threading
from confluent_kafka import Consumer, KafkaError
from database import db
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPICS


def consume_events():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'statistics_service',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(list(KAFKA_TOPICS.values()))
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(msg.error())
                continue

            event = json.loads(msg.value())
            date = event['timestamp'][:10]  # YYYY-MM-DD
            db.execute(
                "INSERT INTO events (event_date, post_id, user_id, event_type) VALUES",
                [(date, event['post_id'], event['user_id'], event['event'])]
            )
    finally:
        consumer.close()


thread = threading.Thread(target=consume_events, daemon=True)
thread.start()

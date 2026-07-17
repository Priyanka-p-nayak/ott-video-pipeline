import json
import time
from datetime import datetime
from kafka import KafkaConsumer
from app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_VIEWER_EVENTS
from app.analytics.db import get_session, init_db
from app.models.event import ViewerEvent
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_consumer(max_retries: int = 10, retry_delay_seconds: int = 3) -> KafkaConsumer:
    for attempt in range(1, max_retries + 1):
        try:
            return KafkaConsumer(
                KAFKA_TOPIC_VIEWER_EVENTS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='analytics-consumer-group',
                enable_auto_commit=True
            )
        except Exception:
            # Generic exception catch ensures compatibility across all kafka-python versions
            logger.warning(f"Kafka not ready yet (attempt {attempt}/{max_retries}), retrying...")
            time.sleep(retry_delay_seconds)
    raise RuntimeError("Could not connect to Kafka after multiple retries")

def handle_event(event_data: dict, partition: int, offset: int) -> None:
    session = get_session()
    try:
        new_event = ViewerEvent(
            video_id=event_data['video_id'],
            event_type=event_data['event'],
            event_timestamp=datetime.fromisoformat(event_data['timestamp']),
            kafka_partition=partition,
            kafka_offset=offset
        )
        session.add(new_event)
        session.commit()
        logger.info(f"Saved event to DB: video_id={new_event.video_id}, id={new_event.id}")
        print(f"[SAVED] {event_data}")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save event to DB: {str(e)} | event={event_data}")
    finally:
        session.close()

def run_consumer_loop() -> None:
    init_db()
    consumer = create_consumer()
    logger.info(f"Consumer started, listening on topic '{KAFKA_TOPIC_VIEWER_EVENTS}'...")
    try:
        for message in consumer:
            handle_event(message.value, message.partition, message.offset)
    except KeyboardInterrupt:
        logger.info("Consumer stopped manually (Ctrl+C)")
    finally:
        consumer.close()
        logger.info("Consumer connection closed cleanly")

if __name__ == '__main__':
    run_consumer_loop()

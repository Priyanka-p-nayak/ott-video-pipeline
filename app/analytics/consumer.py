"""
   Standalone Kafka consumer script for viewer analytics events.
   Reads events from Kafka and persists them into PostgreSQL.

   Run with: python -m app.analytics.consumer
   """

import json
from datetime import datetime
from kafka import KafkaConsumer
from app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_VIEWER_EVENTS
from app.analytics.db import get_session, init_db
from app.models.event import ViewerEvent
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_consumer() -> KafkaConsumer:
       """Create and return a configured KafkaConsumer instance."""
       return KafkaConsumer(
           KAFKA_TOPIC_VIEWER_EVENTS,
           bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
           value_deserializer=lambda v: json.loads(v.decode('utf-8')),
           auto_offset_reset='earliest',
           group_id='analytics-consumer-group',
           enable_auto_commit=True
       )


def handle_event(event_data: dict, partition: int, offset: int) -> None:
       """Process a single consumed event by saving it into PostgreSQL."""
       session = get_session()

       try:
           # Create a Python object representing the new database row
           new_event = ViewerEvent(
               video_id=event_data['video_id'],
               event_type=event_data['event'],
               event_timestamp=datetime.fromisoformat(event_data['timestamp']),
               kafka_partition=partition,
               kafka_offset=offset
           )
           
           # Stage the row for insertion
           session.add(new_event)
           # Actually write it to the database permanently
           session.commit()

           logger.info(
               f"Saved event to DB: video_id={new_event.video_id}, "
               f"event={new_event.event_type}, id={new_event.id}"
           )
           print(f"[SAVED] {event_data}")

       except Exception as e:
           # If anything fails, undo any partial changes to keep the DB clean
           session.rollback()
           logger.error(f"Failed to save event to DB: {str(e)} | event={event_data}")

       finally:
           # ALWAYS close the session to return the connection to the pool
           session.close()


def run_consumer_loop() -> None:
       """Continuously listen for new events and save each one to the database."""
       # Ensure the viewer_events table exists before we start
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
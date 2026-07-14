"""Kafka producer for sending viewer analytics events."""

import json
from kafka import KafkaProducer
from app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_VIEWER_EVENTS
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Module-level singleton: created only once to save connection overhead
_producer = None  


def get_producer() -> KafkaProducer:
    """
    Return a shared KafkaProducer instance, creating it only once.
    Reusing one producer (instead of creating a new one per request)
    is far more efficient — connecting to Kafka has real setup cost.
    """
    global _producer

    if _producer is None:
        logger.info(f"Connecting Kafka producer to {KAFKA_BOOTSTRAP_SERVERS}")
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            # Serialize Python dict -> JSON string -> UTF-8 bytes
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    return _producer


def send_event(event_data: dict) -> bool:
    """
    Send one event dictionary to the viewer-events Kafka topic.
    Returns True if the send was successfully acknowledged, False otherwise.
    """
    try:
        producer = get_producer()
        
        # Queue the message. This returns a 'future' object immediately.
        future = producer.send(KAFKA_TOPIC_VIEWER_EVENTS, value=event_data)
        
        # Block for up to 10 seconds waiting for Kafka to confirm receipt
        result = future.get(timeout=10)  

        logger.info(
            f"Event sent to topic={result.topic}, "
            f"partition={result.partition}, offset={result.offset}"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to send event to Kafka: {str(e)}")
        return False
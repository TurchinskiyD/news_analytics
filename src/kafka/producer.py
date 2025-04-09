
import json
from confluent_kafka import Producer
from src.utils import logger


def create_kafka_producer():
    return Producer({
        'bootstrap.servers': 'localhost:9092'  # або твій Kafka broker
    })


def send_to_kafka(producer, topic, articles):
    for article in articles:
        try:
            producer.produce(topic, key=article["id"], value=json.dumps(article))
        except Exception as e:
            logger.error(f"Kafka send error: {e}")

    producer.flush()

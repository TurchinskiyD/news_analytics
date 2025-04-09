# tests/producer.py

from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

test_event = {
    "source": "test_script",
    "title": "Kafka end-to-end test ✅",
    "timestamp": time.time()
}

producer.send("test_news", value=test_event)
producer.flush()
print("📤 Test event sent to 'test_news'")


# python tests/producer.py
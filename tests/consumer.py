
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'test_news',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',  # читає з самого початку
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🟢 Listening to topic 'test_news'...\n")
for message in consumer:
    print("📩 Received message:")
    print(message.value)
    break  # ✅ читаємо тільки перше повідомлення й виходимо

# python tests/consumer.py

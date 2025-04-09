from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'news_raw',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


print("🟢 Отримуємо всі новини з топіка 'news_raw'...\n")

for i, message in enumerate(consumer):
    print(f"🔹 {i+1}. {message.value['title']}")
    if i >= 9:  # читаємо лише перші 10
        break

# python tests/kafka_read_all.py
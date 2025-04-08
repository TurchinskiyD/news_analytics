#!/bin/bash

set -e

echo "🚀 Запускаємо Kafka через docker-compose..."
docker-compose up -d

echo "⏳ Очікуємо запуск Kafka (10 секунд)..."
sleep 10

echo "🔍 Шукаємо Kafka-контейнер..."
KAFKA_CONTAINER=$(docker ps --filter "name=kafka" --format "{{.ID}}")

if [ -z "$KAFKA_CONTAINER" ]; then
  echo "❌ Kafka контейнер не знайдено. Перевір docker-compose."
  exit 1
fi

echo "🟢 Kafka контейнер знайдено: $KAFKA_CONTAINER"

echo "📌 Створюємо топік 'news_raw'..."
docker exec -it "$KAFKA_CONTAINER" kafka-topics \
  --create \
  --topic news_raw \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1 || echo "⚠️ Можливо, топік уже існує."

echo "📋 Список топіків у Kafka:"
docker exec -it "$KAFKA_CONTAINER" kafka-topics \
  --list \
  --bootstrap-server localhost:9092



# Для запуску
# bash scripts/setup_kafka.sh

#!/bin/bash

set -e

# 👇 Вкажи правильну назву YAML-файлу
COMPOSE_FILE="docker-compose.kafka.yml"

echo "🚀 Запускаємо Kafka з $COMPOSE_FILE ..."
docker-compose -f "$COMPOSE_FILE" up -d

echo "⏳ Очікуємо запуск Kafka (60 секунд)..."
sleep 60

echo "🔍 Шукаємо Kafka-контейнер..."
KAFKA_CONTAINER=$(docker ps --filter "name=kafka" --format "{{.ID}}")

if [ -z "$KAFKA_CONTAINER" ]; then
  echo "❌ Kafka контейнер не знайдено. Перевір docker-compose."
  exit 1
fi

echo "🟢 Kafka контейнер знайдено: $KAFKA_CONTAINER"

#echo "📌 Створюємо топік 'news_raw'..."
#docker exec -it "$KAFKA_CONTAINER" kafka-topics \
#  --create \
#  --topic news_raw \
#  --bootstrap-server localhost:9092 \
#  --partitions 1 \
#  --replication-factor 1 || echo "⚠️ Можливо, топік уже існує."

echo "📋 Список топіків у Kafka:"
docker exec -it "$KAFKA_CONTAINER" kafka-topics \
  --list \
  --bootstrap-server localhost:9092



# Для запуску
# bash scripts/setup_kafka.sh

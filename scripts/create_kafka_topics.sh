#!/bin/bash

KAFKA_CONTAINER=$(docker ps --filter "name=kafka" --format "{{.ID}}")

if [ -z "$KAFKA_CONTAINER" ]; then
  echo "❌ Kafka container not found. Make sure it's running with docker-compose."
  exit 1
fi

echo "🔍 Kafka container ID: $KAFKA_CONTAINER"

docker exec -it "$KAFKA_CONTAINER" kafka-topics --create \
  --topic news_raw \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# для запуску в git bash
# bash scripts/create_kafka_topics.sh

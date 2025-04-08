#!/bin/bash

KAFKA_CONTAINER=$(docker ps --filter "name=kafka" --format "{{.ID}}")

if [ -z "$KAFKA_CONTAINER" ]; then
  echo "❌ Kafka container not found."
  exit 1
fi

echo "🧩 Kafka container ID: $KAFKA_CONTAINER"
echo "📋 Topics in Kafka:"
docker exec -it "$KAFKA_CONTAINER" kafka-topics --list --bootstrap-server localhost:9092


# bash scripts/check_kafka_topics.sh
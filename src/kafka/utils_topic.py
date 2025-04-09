from confluent_kafka.admin import AdminClient, NewTopic


def ensure_topic_exists(topic_name: str, bootstrap_servers: str = "localhost:9092"):
    admin = AdminClient({'bootstrap.servers': bootstrap_servers})
    topic_metadata = admin.list_topics(timeout=5)

    if topic_name not in topic_metadata.topics:
        new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
        fs = admin.create_topics([new_topic])

        for topic, f in fs.items():
            try:
                f.result()  # перевірка на успішне створення
                print(f"✅ Kafka topic created: '{topic}'")
            except Exception as e:
                print(f"❌ Failed to create topic '{topic}': {e}")
    else:
        print(f"ℹ️ Kafka topic already exists: '{topic_name}'")

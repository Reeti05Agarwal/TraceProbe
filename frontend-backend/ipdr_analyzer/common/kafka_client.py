# ipdr_analyzer/common/kafka_client.py
import os
import json
from kafka import KafkaProducer, KafkaConsumer

# Read the Kafka broker address from an environment variable.
# The default 'kafka:29092' is the internal address within Docker.
KAFKA_BROKER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

def create_producer():
    """Creates a new Kafka producer client."""
    print(f"Connecting producer to Kafka at {KAFKA_BROKER}...")
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def create_consumer(topic, group_id):
    """Creates a new Kafka consumer client for a specific topic and group."""
    print(f"Connecting consumer to Kafka at {KAFKA_BROKER} for topic '{topic}'...")
    return KafkaConsumer(
        topic,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

# ipdr_analyzer/consumer/main.py
import os
import json
from elasticsearch import Elasticsearch
from ipdr_analyzer.common.kafka_client import create_consumer

# --- Configuration from Environment Variables ---
KAFKA_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections')
ES_HOST = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
ES_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))
ES_INDEX_NAME = 'ipdr_connections'

# Connect to Elasticsearch using service name
es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}])
print(f"Connecting to Elasticsearch at {ES_HOST}:{ES_PORT}...")

# Create the index if it doesn't exist
if not es.indices.exists(index=ES_INDEX_NAME):
    es.indices.create(index=ES_INDEX_NAME)
    print(f"Created Elasticsearch index: {ES_INDEX_NAME}")

# Connect to Kafka using the common function
consumer = create_consumer(KAFKA_TOPIC, 'es-indexer-group')

print("Elasticsearch consumer started. Listening for processed messages...")

for message in consumer:
    record = message.value # The common consumer already deserializes the JSON
    print(f"Received processed record: {record}")
    try:
        es.index(index=ES_INDEX_NAME, document=record)
        print("Indexed record into Elasticsearch.")
    except Exception as e:
        print(f"Failed to index record. Error: {e}")

# ipdr_analyzer/consumer/main.py
import os
import json
from elasticsearch import Elasticsearch
from ipdr_analyzer.common.kafka_client import create_consumer

# --- Configuration from Environment Variables ---
KAFKA_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections')
ES_HOST = os.getenv('ELASTICSEARCH_HOST', 'elasticsearch')
ES_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))

# Connect to Elasticsearch
es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}])
print(f"Connecting to Elasticsearch at {ES_HOST}:{ES_PORT}...")

# Connect to Kafka
consumer = create_consumer(KAFKA_TOPIC, 'es-indexer-group')
print("Elasticsearch consumer started. Listening for processed messages...")

for message in consumer:
    record = message.value  # JSON already deserialized
    record_count = 0
    # print(f"Received processed record: {record}")

    case_id = record.get('case_id')
    if not case_id:
        print("Skipping record with missing case_id:", record)
        continue

    # Create dynamic index name per case
    es_index_name = f"ipdr_connections_{case_id}"

    # Ensure the index exists 
    try:
        es.indices.create(index=es_index_name)
        print(f"Created Elasticsearch index: {es_index_name}")
    except Exception as e:
        if "resource_already_exists_exception" not in str(e):
            raise

    # Index the record into the case-specific index
    try:
        es.index(index=es_index_name, document=record)
        record_count+=1
        # print(f"Indexed record into {es_index_name}.")
    except Exception as e:
        print(f"Failed to index record into {es_index_name}. Error: {e}")

print("Records indexed: {record_count}")
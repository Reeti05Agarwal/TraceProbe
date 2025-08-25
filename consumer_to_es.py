import json
import logging
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

# --- Enable detailed logging for the Elasticsearch library ---
logging.basicConfig(level=logging.INFO)
logging.getLogger("elasticsearch").setLevel(logging.DEBUG)
logging.getLogger("elastic_transport").setLevel(logging.DEBUG)

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092' # This is correct
KAFKA_TOPIC = 'processed_ipdr_connections'
ES_INDEX_NAME = 'ipdr_connections'

# Connect to Elasticsearch
try:
    print("Attempting to connect to Elasticsearch...")
    es = Elasticsearch(
        'http://localhost:9200',
        # Adding a timeout for safety
        request_timeout=30 
    )
    # Verify the connection
    if not es.ping():
        raise ConnectionError("Ping to Elasticsearch failed.")
    print("Successfully connected to Elasticsearch.")

except Exception as e:
    print(f"An error occurred during Elasticsearch connection: {e}")
    # Exit if we can't connect, and show the full traceback for debugging
    import traceback
    traceback.print_exc()
    exit()


# Create the index if it doesn't exist
try:
    if not es.indices.exists(index=ES_INDEX_NAME):
        es.indices.create(index=ES_INDEX_NAME)
        print(f"Created Elasticsearch index: {ES_INDEX_NAME}")
except Exception as e:
    print(f"Error checking/creating index: {e}")
    exit()


# Connect to Kafka
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='es-indexer-group'
)

print("Elasticsearch consumer started. Listening for processed messages...")

for message in consumer:
    record = message.value
    print(f"Received processed record: {record}")
    try:
        es.index(index=ES_INDEX_NAME, document=record)
        print("Indexed record into Elasticsearch.")
    except Exception as e:
        print(f"Failed to index record. Error: {e}")

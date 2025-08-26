# ipdr_analyzer/processor/main.py
import os
import json
from ipdr_analyzer.common.kafka_client import create_producer, create_consumer

# --- Configuration from Environment Variables ---
SOURCE_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
DESTINATION_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections')

# Create clients using common functions
consumer = create_consumer(SOURCE_TOPIC, 'ipdr-processor-group')
producer = create_producer()

print("Processor started. Listening for messages...")

for message in consumer:
    # The common consumer already deserializes JSON, but our producer sends raw strings.
    # We will decode the message value from bytes to string.
    raw_log = message.value
    print(f"Received raw log: {raw_log}")

    try:
        parts = raw_log.split(',')
        if len(parts) == 5:
            processed_data = {
                "timestamp": parts[0],
                "session_id": parts[1],
                "a_party_ip": parts[2],
                "b_party_ip": parts[3],
                "duration_ms": int(parts[4]),
                "status": "PROCESSED"
            }
            print(f"Processed into JSON: {processed_data}")
            producer.send(DESTINATION_TOPIC, processed_data)

    except Exception as e:
        print(f"Failed to process message: {raw_log}. Error: {e}")

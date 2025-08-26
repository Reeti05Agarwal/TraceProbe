# ipdr_analyzer/producer/main.py
import os
import time
import json
from ipdr_analyzer.common.kafka_client import create_producer

# --- Configuration from Environment Variables ---
KAFKA_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/data/dummy_logs.json') # Path inside the container

# Create a Kafka producer using the common function
# Note: The original producer sent raw strings, this one will send JSON.
producer = KafkaProducer(
    bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')],
    value_serializer=lambda v: v.encode('utf-8')
)

print(f"Producer started. Reading from {LOG_FILE_PATH} and sending to topic '{KAFKA_TOPIC}'...")

# Wait for the file to be available (useful in Docker)
while not os.path.exists(LOG_FILE_PATH):
    print(f"Waiting for log file at {LOG_FILE_PATH}...")
    time.sleep(2)

try:
    with open(LOG_FILE_PATH, 'r') as f:
        for line in f:
            log_entry = line.strip()
            if log_entry:
                print(f"Sending log: {log_entry}")
                producer.send(KAFKA_TOPIC, log_entry)
                time.sleep(0.1)

    producer.flush()
    print("Finished sending all logs.")

except FileNotFoundError:
    print(f"Error: The file '{LOG_FILE_PATH}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    producer.close()

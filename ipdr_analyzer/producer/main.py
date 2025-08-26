import os
import time
import json
# Use the function from our common client to create a producer
from ipdr_analyzer.common.kafka_client import create_producer

# --- Configuration from Environment Variables ---
KAFKA_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/data/dummy_logs.json')

# Create a Kafka producer using the robust common function
producer = create_producer()

print(f"Producer started. Reading from {LOG_FILE_PATH} and sending to topic '{KAFKA_TOPIC}'...")

# Wait for the file to be available
while not os.path.exists(LOG_FILE_PATH):
    print(f"Waiting for log file at {LOG_FILE_PATH}...")
    time.sleep(2)

try:
    with open(LOG_FILE_PATH, 'r') as f:
        for line in f:
            log_entry = line.strip()
            if log_entry:
                # Our new producer sends JSON, so we wrap the log in a dictionary
                message = {'log': log_entry}
                print(f"Sending log: {json.dumps(message)}")
                producer.send(KAFKA_TOPIC, value=message)
                time.sleep(0.1)

    producer.flush()
    print("Finished sending all logs.")

except FileNotFoundError:
    print(f"Error: The file '{LOG_FILE_PATH}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if producer:
        producer.close()

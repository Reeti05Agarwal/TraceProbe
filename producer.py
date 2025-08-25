import time
from kafka import KafkaProducer

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'raw_ipdr_logs'
LOG_FILE_PATH = 'dummy_logs.json'  # Make sure your log file is in the same folder

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    # Encode messages as bytes
    value_serializer=lambda v: v.encode('utf-8')
)

print(f"Producer started. Reading from {LOG_FILE_PATH} and sending to Kafka topic '{KAFKA_TOPIC}'...")

try:
    with open(LOG_FILE_PATH, 'r') as f:
        for line in f:
            log_entry = line.strip()
            if log_entry: # Ensure we don't send empty lines
                print(f"Sending log: {log_entry}")
                producer.send(KAFKA_TOPIC, log_entry)
                time.sleep(0.1) # Slow down for demonstration purposes

    producer.flush() # Ensure all messages are sent
    print("Finished sending all logs.")

except FileNotFoundError:
    print(f"Error: The file '{LOG_FILE_PATH}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    producer.close()

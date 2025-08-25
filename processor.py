import json
from kafka import KafkaConsumer, KafkaProducer

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'
SOURCE_TOPIC = 'raw_ipdr_logs'
DESTINATION_TOPIC = 'processed_ipdr_connections'

# Create a consumer to read raw logs
consumer = KafkaConsumer(
    SOURCE_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest', # Start reading from the beginning of the topic
    group_id='ipdr-processor-group'
)

# Create a producer to send processed data
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    # Serialize our dictionary to a JSON string, then encode to bytes
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Processor started. Listening for messages...")

for message in consumer:
    raw_log = message.value.decode('utf-8')
    print(f"Received raw log: {raw_log}")

    try:
        # --- THIS IS YOUR CORE LOGIC ---
        # For this prototype, we'll just split a CSV string.
        # In the real project, this is where you'd implement your
        # complex parsing and A-Party to B-Party mapping from Flink.
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

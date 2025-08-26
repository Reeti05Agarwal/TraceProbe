import os
import json
from ipdr_analyzer.common.kafka_client import create_producer, create_consumer

# --- Configuration ---
SOURCE_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
# This topic should feed the Elasticsearch sink connector
DESTINATION_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections') 

# Create clients
consumer = create_consumer(SOURCE_TOPIC, 'ipdr-processor-group')
producer = create_producer()

print("✅ Processor started. Listening for messages...")

for message in consumer:
    # message.value is already a dictionary, e.g., {'log': '{"record_id": ...}'}
    raw_log_dict = message.value
    
    try:
        # 1. Get the JSON string from the 'log' key. Use .get() for safety.
        log_string = raw_log_dict.get('log')
        if not log_string:
            print(f"⚠️ Skipping message with no 'log' key: {raw_log_dict}")
            continue

        # 2. Parse that string into a proper dictionary
        log_data = json.loads(log_string)

        # 3. Extract the A-Party (initiator) and B-Party (recipient) details
        # The A-Party is the subscriber, identified by their public NAT IP or mobile number
        # The B-Party is the destination IP they are connecting to
        processed_data = {
            "timestamp": log_data.get("timestamp_start"),
            "session_id": log_data.get("aaa_session_id"),
            "a_party_nat_ip": log_data.get("nat_public_ip"), # User's Public IP
            "a_party_msisdn": log_data.get("msisdn"),       # User's Mobile Number
            "b_party_ip": log_data.get("dst_ip"),           # Destination Public IP
            "b_party_domain": log_data.get("domain"),
            "duration_sec": log_data.get("duration_sec"),
            "app_protocol": log_data.get("app_proto"),
            "access_city": log_data.get("access_city"),
            "server_country": log_data.get("server_country")
        }
        
        # 4. Send the clean, processed JSON to the destination topic
        producer.send(DESTINATION_TOPIC, processed_data)
        print(f"Successfully processed and sent connection: {processed_data['a_party_nat_ip']} -> {processed_data['b_party_ip']}")

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string: {log_string}. Error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {raw_log_dict}. Error: {e}")

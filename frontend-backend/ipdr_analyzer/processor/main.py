# ipdr_analyzer/processor/main.py
import os
import json
from ipdr_analyzer.common.kafka_client import create_producer, create_consumer

SOURCE_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
DESTINATION_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections') 

consumer = create_consumer(SOURCE_TOPIC, 'ipdr-processor-group')
producer = create_producer()

print("✅ Processor started. Listening for messages...")

for message in consumer:
    raw_log_dict = message.value
    try:
        log_string = raw_log_dict.get('log')
        if not log_string:
            print(f"⚠️ Skipping message with no 'log' key: {raw_log_dict}")
            continue

        log_data = json.loads(log_string)  # now a dict
        case_id = raw_log_dict.get('case_id')

        processed_data = {
            # 1. Identification & Timing
            "id_record": log_data.get("record_id"),
            "case_id": case_id,
            "time_start": log_data.get("timestamp_start"),
            "time_end": log_data.get("timestamp_end"),
            "time_duration_sec": log_data.get("duration_sec"),

            # 2. Subscriber & Access Info
            "sub_id": log_data.get("subscriber_id"),
            "sub_msisdn": log_data.get("msisdn"),
            "sub_imsi": log_data.get("imsi"),
            "sub_imei": log_data.get("imei"),
            "access_city": log_data.get("access_city"),
            "access_country": log_data.get("access_country"),

            # 3. Source / Client Info
            "src_ip": log_data.get("src_ip"),
            "src_nat_ip": log_data.get("nat_public_ip"),
            "src_port": log_data.get("src_port"),
            "src_device_type": log_data.get("device_type"),
            "src_device_os": log_data.get("device_os"),

            # 4. Destination / Remote Info
            "dst_ip": log_data.get("dst_ip"),
            "dst_port": log_data.get("dst_port"),
            "dst_domain": log_data.get("domain"),
            "dst_server_country": log_data.get("server_country"),
            "dst_server_asn": log_data.get("server_asn"),

            # 5. NAT / CGNAT Mapping
            "nat_session_id": log_data.get("nat_session_id"),
            "nat_port": log_data.get("nat_public_port"),
            "nat_box_id": log_data.get("cgnat_box_id"),

            # 6. Protocol & Traffic
            "proto_l4": log_data.get("l4_proto"),
            "proto_app": log_data.get("app_proto"),
            "proto_bytes_up": log_data.get("bytes_up"),
            "proto_bytes_down": log_data.get("bytes_down"),
            "proto_pkts_up": log_data.get("pkts_up"),
            "proto_pkts_down": log_data.get("pkts_down"),
            "proto_policy_action": log_data.get("policy_action"),

            # 7. DNS & Threat Intel
            "dns_query": log_data.get("dns_query"),
            "dns_response_ip": log_data.get("dns_response_ip"),
            "threat_indicator": log_data.get("threat_indicator"),
            "threat_feed": log_data.get("threat_feed"),
            "threat_severity": log_data.get("threat_severity"),
        }

    

        producer.send(DESTINATION_TOPIC, processed_data)
        print(f"Processed connection: {processed_data['src_nat_ip']} -> {processed_data['dst_ip']} (case={case_id})")

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string: {log_string}. Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e} ; raw: {raw_log_dict}")

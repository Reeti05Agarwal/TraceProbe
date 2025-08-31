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
            "id_record": str(log_data.get("record_id", "")),
            "case_id": str(case_id) if case_id is not None else None,
            "time_start": str(log_data.get("timestamp_start", "")),
            "time_end": str(log_data.get("timestamp_end", "")),
            "time_duration_sec": float(log_data.get("duration_sec", 0.0)),

            # 2. Subscriber & Access Info
            "sub_id": str(log_data.get("subscriber_id", "")),
            "sub_msisdn": str(log_data.get("msisdn", "")),
            "sub_imsi": str(log_data.get("imsi", "")),
            "sub_imei": str(log_data.get("imei", "")),
            "access_city": str(log_data.get("access_city", "")),
            "access_country": str(log_data.get("access_country", "")),

            # 3. Source / Client Info
            "src_ip": str(log_data.get("src_ip", "")),
            "src_nat_ip": str(log_data.get("nat_public_ip", "")),
            "src_port": int(log_data.get("src_port", 0)),
            "src_device_type": str(log_data.get("device_type", "")),
            "src_device_os": str(log_data.get("device_os", "")),

            # 4. Destination / Remote Info
            "dst_ip": str(log_data.get("dst_ip", "")),
            "dst_port": int(log_data.get("dst_port", 0)),
            "dst_domain": str(log_data.get("domain", "")),
            "dst_server_country": str(log_data.get("server_country", "")),
            "dst_server_asn": int(log_data.get("server_asn", 0)),

            # 5. NAT / CGNAT Mapping
            "nat_session_id": str(log_data.get("nat_session_id", "")),
            "nat_port": int(log_data.get("nat_public_port", 0)),
            "nat_box_id": str(log_data.get("cgnat_box_id", "")),

            # 6. Protocol & Traffic
            "proto_l4": str(log_data.get("l4_proto", "")),
            "proto_app": str(log_data.get("app_proto", "")),
            "proto_bytes_up": float(log_data.get("bytes_up", 0.0)),
            "proto_bytes_down": float(log_data.get("bytes_down", 0.0)),
            "proto_pkts_up": int(log_data.get("pkts_up", 0)),
            "proto_pkts_down": int(log_data.get("pkts_down", 0)),
            "proto_policy_action": str(log_data.get("policy_action", "")),

            # 7. DNS & Threat Intel
            "dns_query": str(log_data.get("dns_query", "")),
            "dns_response_ip": str(log_data.get("dns_response_ip", "")),
            "threat_indicator": str(log_data.get("threat_indicator", "")),
            "threat_feed": str(log_data.get("threat_feed", "")),
            "threat_severity": float(log_data.get("threat_severity", 0.0)),
        }

        producer.send(DESTINATION_TOPIC, processed_data)
        print(f"Processed connection: {processed_data['src_nat_ip']} -> {processed_data['dst_ip']} (case={case_id})")

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string: {log_string}. Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e} ; raw: {raw_log_dict}")

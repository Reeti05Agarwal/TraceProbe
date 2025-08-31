import os
import json
from ipdr_analyzer.common.kafka_client import create_producer, create_consumer

# --- Configuration ---
SOURCE_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
DESTINATION_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections') 

# Create clients
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

        log_data = json.loads(log_string)

        # Core + extended fields
        processed_data = {
            # --- Identification & Tracking ---
            "record_id": log_data.get("record_id"),
            "collector_receive_time": log_data.get("collector_receive_time"),
            "ingest_source": log_data.get("ingest_source"),

            # --- Subscriber Info ---
            "subscriber_id": log_data.get("subscriber_id"),
            "enterprise_tenant_id": log_data.get("enterprise_tenant_id"),
            "pii_masked": log_data.get("pii_masked"),
            "quota_consumed_mb": log_data.get("quota_consumed_mb"),

            # --- Session / Event ---
            "event_type": log_data.get("event_type"),
            "timestamp_start": log_data.get("timestamp_start"),
            "timestamp_end": log_data.get("timestamp_end"),
            "session_id": log_data.get("aaa_session_id"),
            "duration_sec": log_data.get("duration_sec"),

            # --- Network Access ---
            "access_type": log_data.get("access_type"),
            "bng_id": log_data.get("bng_id"),
            "nas_ip": log_data.get("nas_ip"),
            "nas_port": log_data.get("nas_port"),
            "pop_id": log_data.get("pop_id"),
            "access_country": log_data.get("access_country"),
            "access_city": log_data.get("access_city"),
            "access_longitude": log_data.get("access_longitude"),
            "access_latitude": log_data.get("access_latitude"),

            # --- Client / Device ---
            "src_ip": log_data.get("src_ip"),
            "src_port": log_data.get("src_port"),
            "src_mac": log_data.get("src_mac"),
            "device_type": log_data.get("device_type"),
            "device_os": log_data.get("device_os"),
            "user_agent": log_data.get("user_agent"),
            "imsi": log_data.get("imsi"),
            "imei": log_data.get("imei"),
            "msisdn": log_data.get("msisdn"),
            "apn": log_data.get("apn"),
            "cell_id": log_data.get("cell_id"),

            # --- Destination / Remote ---
            "dst_ip": log_data.get("dst_ip"),
            "dst_port": log_data.get("dst_port"),
            "domain": log_data.get("domain"),
            "server_asn": log_data.get("server_asn"),
            "server_country": log_data.get("server_country"),
            "server_city": log_data.get("server_city"),

            # --- NAT / CGNAT ---
            "nat_session_id": log_data.get("nat_session_id"),
            "nat_public_ip": log_data.get("nat_public_ip"),
            "nat_public_port": log_data.get("nat_public_port"),
            "nat_pool_id": log_data.get("nat_pool_id"),
            "cgnat_box_id": log_data.get("cgnat_box_id"),

            # --- Protocol & Traffic ---
            "l3_proto": log_data.get("l3_proto"),
            "l4_proto": log_data.get("l4_proto"),
            "app_proto": log_data.get("app_proto"),
            "tls_cipher": log_data.get("tls_cipher"),
            "qos_class": log_data.get("qos_class"),
            "policy_id": log_data.get("policy_id"),
            "policy_action": log_data.get("policy_action"),
            "bytes_up": log_data.get("bytes_up"),
            "bytes_down": log_data.get("bytes_down"),
            "pkts_up": log_data.get("pkts_up"),
            "pkts_down": log_data.get("pkts_down"),
            "tcp_syn": log_data.get("tcp_syn"),
            "tcp_fin": log_data.get("tcp_fin"),
            "tcp_rst": log_data.get("tcp_rst"),
            "tcp_retrans": log_data.get("tcp_retrans"),

            # --- DNS / Application ---
            "dns_query": log_data.get("dns_query"),
            "dns_response_ip": log_data.get("dns_response_ip"),
            "dns_rcode": log_data.get("dns_rcode"),

            # --- Threat / Security ---
            "threat_indicator": log_data.get("threat_indicator"),
            "threat_feed": log_data.get("threat_feed"),
            "threat_severity": log_data.get("threat_severity"),
            "threat_confidence": log_data.get("threat_confidence"),
        }

        producer.send(DESTINATION_TOPIC, processed_data)
        print(f"✅ Processed: {processed_data['src_ip']} ({processed_data['nat_public_ip']}) -> {processed_data['dst_ip']}")

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string: {log_string}. Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {raw_log_dict}. Error: {e}")

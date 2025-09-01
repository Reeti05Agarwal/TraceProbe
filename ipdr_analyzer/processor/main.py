# ipdr_analyzer/processor/main.py
import os
import json
import socket
from collections import defaultdict
from ipdr_analyzer.common.kafka_client import create_producer, create_consumer
from ipdr_analyzer.processor.rule_based.bogon import is_bogon
from ipdr_analyzer.processor.rule_based.geo_lookup import get_geo
from ipdr_analyzer.processor.rule_based.sub_entropy import ip_entropy
# from ipdr_analyzer.processor.rule_based.abuseipdb import abuseipdb_score 

# Maintain subscriber IP history for entropy calculation
subscriber_ip_history = defaultdict(list)

# Kafka topics
SOURCE_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')
DESTINATION_TOPIC = os.getenv('KAFKA_PROCESSED_TOPIC', 'processed_ipdr_connections') 

# Kafka clients
consumer = create_consumer(SOURCE_TOPIC, 'ipdr-processor-group', start_from_latest=True)
producer = create_producer()

print("✅ Processor started. Listening for messages...")


# --- Helper functions for enrichment ---

# TTL anomaly: compute difference from expected TTL
def ttl_anomaly_score(ttl, expected_ttl=64):
    try:
        return abs(int(ttl) - expected_ttl)
    except:
        return None

# ASN mismatch: compare IP ASN to subscriber ISP ASN
def asn_mismatch(ip_asn, subscriber_asn):
    if ip_asn is None or subscriber_asn is None:
        return None
    return 0 if ip_asn == subscriber_asn else 1

# Blacklist check: call an API or lookup table
def is_blacklisted_ip(ip):
    # TODO: replace with AbuseIPDB / threat feed
    blacklisted_ips = {"1.2.3.4", "5.6.7.8", "119.135.22.68", "205.221.5.38"}
    return 1 if ip in blacklisted_ips else 0

# Reverse DNS mismatch check
def rdns_mismatch(ip, expected_patterns=None):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        if expected_patterns:
            for pattern in expected_patterns:
                if pattern in hostname:
                    return 0
        return 1  # mismatch
    except:
        return 1  # unable to resolve or mismatch

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

        # --- Rule-Based Enrichment ---
        src_ip = processed_data['src_ip']
        subscriber_id = processed_data['sub_id']

        # Bogon / Reserved IP check
        processed_data['bogon_flag'] = is_bogon(src_ip)

        # Geo lookup
        country, lat, lon = get_geo(src_ip)
        processed_data['geo_country'] = country
        processed_data['geo_lat'] = lat
        processed_data['geo_lon'] = lon

        # Update subscriber IP history & compute entropy
        subscriber_ip_history[subscriber_id].append(src_ip)
        processed_data['entropy'] = ip_entropy(subscriber_ip_history[subscriber_id])

        # Placeholder for TTL anomaly
        processed_data['ttl_anomaly'] = ttl_anomaly_score(log_data.get("ttl"))

        # Placeholder for ASN mismatch
        processed_data['asn_mismatch'] = asn_mismatch(
            log_data.get("src_asn"),  # IP ASN
            log_data.get("subscriber_asn")  # subscriber ISP ASN
        )

        # Placeholder for blacklist / rDNS
        processed_data['blacklist_score_ip'] = int(is_blacklisted_ip(src_ip) or 0)
        # processed_data['blacklist_score_abuseipdb'] = int(abuseipdb_score(src_ip) or 0)
        processed_data['rDNS_mismatch'] = int(rdns_mismatch(src_ip) or 1)

        # Send enriched record to processed topic
        producer.send(DESTINATION_TOPIC, processed_data)
        print(f"✅ Processed & enriched: {processed_data['src_nat_ip']} -> {processed_data['dst_ip']} (case={case_id})")

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string: {log_string}. Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e} ; raw: {raw_log_dict}")

 ISP-provided IPDR logs
 
 
### **1. Identification & Record Tracking**

| Field                    | Use in Investigation                                                                          |
| ------------------------ | --------------------------------------------------------------------------------------------- |
| `record_id`              | Unique identifier for each IPDR record, helps in tracing and referencing specific sessions.   |
| `schema_version`         | Ensures analysts know the data format; critical when comparing records over time.             |
| `collector_receive_time` | Time the network collector received the record; helps detect delays or discrepancies.         |
| `ingest_source`          | Identifies which monitoring system collected the record; useful for system audits.            |
| `processing_node`        | Node that processed the record; relevant for debugging or tracing data flow.                  |
| `checksum`               | Verifies integrity of the record to prevent tampering.                                        |
| `deduped`                | Indicates whether duplicate records were removed, important when counting events or sessions. |

---

### **2. Subscriber & Account Info**

| Field                  | Use                                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| `subscriber_id`        | Pseudonymous identifier for a user; allows tracking user activity while masking real identity. |
| `account_number`       | Masked billing account; links network activity to billing info.                                |
| `customer_type`        | Retail, enterprise, government; provides context on user profile.                              |
| `enterprise_tenant_id` | Tenant ID for enterprises/government; identifies organizational subscribers.                   |
| `pii_masked`           | Indicates if personally identifiable information is masked, relevant for legal compliance.     |
| `service_plan`         | User’s plan tier; can indicate expected traffic patterns or restrictions.                      |
| `quota_consumed_mb`    | Measures data consumption; unusual spikes may indicate malicious activity.                     |
| `billing_rated`        | Whether traffic is billed; can help correlate financial logs.                                  |

---

### **3. Session / Event Timing**

| Field                               | Use                                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------------------- |
| `event_type`                        | Type of session (flow, DNS, NAT, threat, policy, etc.); defines context of the record.      |
| `timestamp_start` / `timestamp_end` | Start and end of session; allows timeline reconstruction.                                   |
| `aaa_session_id`                    | Session ID from AAA (RADIUS/DIAMETER); helps link network session to authentication events. |
| `aaa_start_time` / `aaa_end_time`   | AAA authentication session timing; can be correlated with access logs.                      |
| `duration_sec`                      | Total duration; identifies unusually long or short sessions.                                |
| `collector_receive_time`            | See above, useful for cross-verification of timestamps.                                     |

---

### **4. Network & Access Details**

| Field                                                                  | Use                                                                                    |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `access_type`                                                          | FTTH/DSL/WiFi/4G/5G; indicates access medium.                                          |
| `bng_id`                                                               | Broadband network gateway; helps locate network segment.                               |
| `nas_ip` / `nas_port`                                                  | Network Access Server info; identifies device serving the session.                     |
| `vlan_id`                                                              | Access VLAN ID; helps map network topology.                                            |
| `pppoe_session_id` / `dhcp_lease_id`                                   | Specific session identifiers; crucial for ISP correlation.                             |
| `pop_id`                                                               | Point-of-presence ID; useful for geolocation.                                          |
| `access_country`, `access_city`, `access_longitude`, `access_latitude` | Approximate physical location of user; can help identify origin of malicious activity. |

---

### **5. Client / Device Info**

| Field                                      | Use                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------- |
| `src_ip` / `src_ipv6`                      | Client’s private IP; starting point for network trace.                    |
| `src_port`                                 | Source port; can indicate type of connection.                             |
| `src_mac`                                  | MAC address (if visible); identifies device hardware.                     |
| `device_os`                                | Device operating system; useful to detect exploits targeting OS.          |
| `device_type`                              | Category of device (PC, IoT, mobile); helps detect abnormal devices.      |
| `user_agent`                               | HTTP user agent; helps identify browsers or automated scripts.            |
| `imsi`, `imei`, `msisdn`, `apn`, `cell_id` | Mobile-specific identifiers; used for tracing mobile network subscribers. |

---

### **6. Destination / Remote Info**

|Field|Use|
|---|---|
|`dst_ip` / `dst_ipv6`|Destination IP; critical for identifying target of activity.|
|`dst_port`|Destination port; helps determine service/protocol accessed.|
|`domain`|Resolved domain; identifies accessed website or service.|
|`server_asn`, `server_country`, `server_city`|Information about destination network; helps in geo-targeting, threat attribution.|

---

### **7. NAT / CGNAT Info**

| Field                                                | Use                                                                        |
| ---------------------------------------------------- | -------------------------------------------------------------------------- |
| `nat_session_id`, `nat_public_ip`, `nat_public_port` | Maps private IP to public IP and port; essential for tracing through NATs. |
| `nat_pool_id`, `cgnat_box_id`                        | Identifies NAT device or pool; helps map egress IP to subscriber.          |

---

### **8. Protocol & Traffic Details**

|Field|Use|
|---|---|
|`l3_proto` / `l4_proto`|Layer 3/4 protocols (IPv4/6, TCP/UDP); useful for filtering and identifying attack vectors.|
|`app_proto`|DPI-detected protocol; helps identify application layer activity.|
|`tls_cipher`|Encryption used; can help analyze secure connections.|
|`qos_class`|Quality of Service; abnormal QoS usage may indicate misuse.|
|`policy_id` / `policy_action`|Applied network policies; shows if traffic was blocked or allowed.|
|`bytes_up`, `bytes_down`, `pkts_up`, `pkts_down`|Traffic volume; anomalies may indicate data exfiltration.|
|`tcp_syn`, `tcp_fin`, `tcp_rst`, `tcp_retrans`|TCP control flags; detect scanning, connection resets, or retransmission attacks.|
|`latency_ms`, `jitter_ms`, `loss_pct`|Network performance; anomalies can indicate network tampering or DoS.|

---

### **9. DNS / Application Queries**

|Field|Use|
|---|---|
|`dns_query`, `dns_response_ip`, `dns_rcode`|DNS requests/responses; can detect domain abuse, phishing, or malware C2 communication.|

---

### **10. Threat & Security Indicators**

|Field|Use|
|---|---|
|`threat_indicator`, `threat_feed`|Type and source of threat intel; flags malicious activity.|
|`threat_severity`, `threat_confidence`|Helps prioritize investigations; quantify risk level.|
|`warrant_case_id`|Legal context linking record to investigation.|
|`access_purpose`|Purpose of network access; aids in compliance verification.|
|`confidence`|Classifier confidence in detection; helps analysts trust automated insights.|

---

### Summary

Essentially, IPDR data helps investigators:

1. **Trace user activity** through subscriber IDs, IPs, NAT info, and timestamps.
    
2. **Identify endpoints and devices** via OS, MAC, and device type.
    
3. **Analyze traffic patterns** using protocol, QoS, bytes/packets, and TCP flags.
    
4. **Correlate with threat intelligence** using threat feeds, severity, and domain info.
    
5. **Support legal investigations** using masked identifiers, warrants, and AAA session info.
    
 













# Schema

[

  {

    "name": "record_id",

    "desc": "Unique identifier for the IPDR/XDR record (UUID)"

  },

  {

    "name": "event_type",

    "desc": "Type of event (flow/session/dns/nat/policy/threat)"

  },

  {

    "name": "timestamp_start",

    "desc": "UTC start time of session/flow"

  },

  {

    "name": "timestamp_end",

    "desc": "UTC end time of session/flow"

  },

  {

    "name": "collector_receive_time",

    "desc": "Collector receive time"

  },

  {

    "name": "ingest_source",

    "desc": "Source system (e.g., dpi-delhi-01)"

  },

  {

    "name": "schema_version",

    "desc": "Internal schema version"

  },

  {

    "name": "subscriber_id",

    "desc": "Pseudonymous subscriber identifier"

  },

  {

    "name": "account_number",

    "desc": "Billing account number (masked)"

  },

  {

    "name": "customer_type",

    "desc": "Retail/Enterprise/Government"

  },

  {

    "name": "enterprise_tenant_id",

    "desc": "Enterprise/government tenant id"

  },

  {

    "name": "pii_masked",

    "desc": "Whether PII is masked"

  },

  {

    "name": "aaa_session_id",

    "desc": "AAA session id (RADIUS/DIAMETER)"

  },

  {

    "name": "aaa_start_time",

    "desc": "AAA session start"

  },

  {

    "name": "aaa_end_time",

    "desc": "AAA session end"

  },

  {

    "name": "access_type",

    "desc": "FTTH/DSL/DOCSIS/WiFi/4G/5G"

  },

  {

    "name": "bng_id",

    "desc": "BNG/BRAS id"

  },

  {

    "name": "nas_ip",

    "desc": "NAS IP"

  },

  {

    "name": "nas_port",

    "desc": "NAS port/interface"

  },

  {

    "name": "vlan_id",

    "desc": "Access VLAN id"

  },

  {

    "name": "pppoe_session_id",

    "desc": "PPPoE session id"

  },

  {

    "name": "dhcp_lease_id",

    "desc": "DHCP lease id"

  },

  {

    "name": "src_ip",

    "desc": "Client/private IP"

  },

  {

    "name": "src_port",

    "desc": "Client source port"

  },

  {

    "name": "src_ipv6",

    "desc": "Client IPv6"

  },

  {

    "name": "src_mac",

    "desc": "Client MAC (if visible)"

  },

  {

    "name": "device_os",

    "desc": "Client OS"

  },

  {

    "name": "device_type",

    "desc": "Device category"

  },

  {

    "name": "user_agent",

    "desc": "HTTP user agent (if any)"

  },

  {

    "name": "dst_ip",

    "desc": "Destination IP"

  },

  {

    "name": "dst_port",

    "desc": "Destination port"

  },

  {

    "name": "dst_ipv6",

    "desc": "Destination IPv6"

  },

  {

    "name": "domain",

    "desc": "Resolved domain"

  },

  {

    "name": "server_asn",

    "desc": "Destination ASN"

  },

  {

    "name": "server_country",

    "desc": "Server country"

  },

  {

    "name": "server_city",

    "desc": "Server city"

  },

  {

    "name": "nat_session_id",

    "desc": "CGNAT session id"

  },

  {

    "name": "nat_public_ip",

    "desc": "Egress public IP"

  },

  {

    "name": "nat_public_port",

    "desc": "Egress public port"

  },

  {

    "name": "nat_pool_id",

    "desc": "NAT pool id"

  },

  {

    "name": "cgnat_box_id",

    "desc": "CGNAT device id"

  },

  {

    "name": "l3_proto",

    "desc": "IPv4/IPv6/DualStack"

  },

  {

    "name": "l4_proto",

    "desc": "TCP/UDP/ICMP/..."

  },

  {

    "name": "app_proto",

    "desc": "Application protocol (DPI)"

  },

  {

    "name": "tls_cipher",

    "desc": "TLS cipher (if encrypted)"

  },

  {

    "name": "qos_class",

    "desc": "QoS/DSCP class"

  },

  {

    "name": "policy_id",

    "desc": "Matched policy id"

  },

  {

    "name": "policy_action",

    "desc": "Policy action"

  },

  {

    "name": "bytes_up",

    "desc": "Bytes up"

  },

  {

    "name": "bytes_down",

    "desc": "Bytes down"

  },

  {

    "name": "pkts_up",

    "desc": "Packets up"

  },

  {

    "name": "pkts_down",

    "desc": "Packets down"

  },

  {

    "name": "duration_sec",

    "desc": "Duration seconds"

  },

  {

    "name": "tcp_syn",

    "desc": "TCP SYN count"

  },

  {

    "name": "tcp_fin",

    "desc": "TCP FIN count"

  },

  {

    "name": "tcp_rst",

    "desc": "TCP RST count"

  },

  {

    "name": "tcp_retrans",

    "desc": "TCP retransmissions"

  },

  {

    "name": "latency_ms",

    "desc": "RTT latency ms"

  },

  {

    "name": "jitter_ms",

    "desc": "Jitter ms"

  },

  {

    "name": "loss_pct",

    "desc": "Loss percentage"

  },

  {

    "name": "dns_query",

    "desc": "DNS query (if DNS)"

  },

  {

    "name": "dns_response_ip",

    "desc": "DNS response IP"

  },

  {

    "name": "dns_rcode",

    "desc": "DNS response code"

  },

  {

    "name": "imsi",

    "desc": "IMSI (mobile optional)"

  },

  {

    "name": "imei",

    "desc": "IMEI (mobile optional)"

  },

  {

    "name": "msisdn",

    "desc": "MSISDN (masked)"

  },

  {

    "name": "apn",

    "desc": "APN (mobile)"

  },

  {

    "name": "cell_id",

    "desc": "Cell id (mobile)"

  },

  {

    "name": "pop_id",

    "desc": "Point-of-presence id"

  },

  {

    "name": "access_country",

    "desc": "Access country"

  },

  {

    "name": "access_city",

    "desc": "Access city"

  },

  {

    "name": "access_longitude",

    "desc": "Longitude approx"

  },

  {

    "name": "access_latitude",

    "desc": "Latitude approx"

  },

  {

    "name": "threat_indicator",

    "desc": "Threat indicator type"

  },

  {

    "name": "threat_feed",

    "desc": "Threat intel feed"

  },

  {

    "name": "threat_severity",

    "desc": "Severity 0-10"

  },

  {

    "name": "threat_confidence",

    "desc": "Confidence 0-1"

  },

  {

    "name": "service_plan",

    "desc": "Plan tier"

  },

  {

    "name": "quota_consumed_mb",

    "desc": "Quota consumed MB"

  },

  {

    "name": "billing_rated",

    "desc": "Rated for billing"

  },

  {

    "name": "warrant_case_id",

    "desc": "Warrant/case id"

  },

  {

    "name": "access_purpose",

    "desc": "Purpose for access"

  },

  {

    "name": "confidence",

    "desc": "Classifier confidence 0-1"

  },

  {

    "name": "deduped",

    "desc": "Was record deduped"

  },

  {

    "name": "checksum",

    "desc": "Record checksum"

  },

  {

    "name": "processing_node",

    "desc": "Processing node id"

  }

]
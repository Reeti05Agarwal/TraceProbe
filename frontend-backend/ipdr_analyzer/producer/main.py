# ipdr_analyzer/producer/main.py
import os
import sys
import time
import json
import csv
import pandas as pd
from ipdr_analyzer.common.kafka_client import create_producer

KAFKA_TOPIC = os.getenv('KAFKA_RAW_LOGS_TOPIC', 'raw_ipdr_logs')

# Accept file path and optional case_id as CLI args
if len(sys.argv) < 2:
    print("Usage: python main.py <log_file_path> [case_id]")
    sys.exit(1)

LOG_FILE_PATH = sys.argv[1]
CASE_ID = sys.argv[2] if len(sys.argv) > 2 else None

producer = create_producer()
print(f"Producer started. Reading from {LOG_FILE_PATH} and sending to topic '{KAFKA_TOPIC}' (case_id={CASE_ID})...")

try:
    file_ext = os.path.splitext(LOG_FILE_PATH)[1].lower()

    if file_ext == ".json":
        with open(LOG_FILE_PATH, 'r') as f:
            for line in f:
                log_entry = line.strip()
                if log_entry:
                    # keep string form; downstream expects JSON string
                    message = {'log': log_entry}
                    if CASE_ID:
                        message['case_id'] = CASE_ID
                    producer.send(KAFKA_TOPIC, value=message)
                    time.sleep(0.01)

    elif file_ext == ".csv":
        with open(LOG_FILE_PATH, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                message = {'log': json.dumps(row)}
                if CASE_ID:
                    message['case_id'] = CASE_ID
                producer.send(KAFKA_TOPIC, value=message)
                time.sleep(0.01)

    elif file_ext in [".xls", ".xlsx"]:
        df = pd.read_excel(LOG_FILE_PATH)
        for _, row in df.iterrows():
            message = {'log': json.dumps(row.to_dict())}
            if CASE_ID:
                message['case_id'] = CASE_ID
            producer.send(KAFKA_TOPIC, value=message)
            time.sleep(0.01)
    else:
        print(f"Unsupported file type: {file_ext}")

    producer.flush()
    print("Finished sending all logs.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    try:
        producer.close()
    except:
        pass

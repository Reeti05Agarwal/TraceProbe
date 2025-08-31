Of course\! Here is a complete `README.md` file for your project. You can copy and paste this directly into a file named `README.md` in the root of your project directory.

-----

Frontend UI → http://localhost:3000

Backend API → http://localhost:8000/api

Kibana → http://localhost:5601

Elasticsearch → http://localhost:9200


# IPDR FlowAnalyzer: Log Analysis & Mapping Tool 🕵️‍♂️

This project is a real-time data pipeline designed to ingest, process, and analyze massive volumes of IPDR (Internet Protocol Detail Record) logs. It helps law enforcement investigators identify and visualize communication patterns, mapping connections between parties of interest.

## Tech Stack 🛠️

  * **Data Ingestion & Processing:** Python
  * **Message Broker:** Apache Kafka
  * **Search & Analytics Engine:** Elasticsearch
  * **Visualization:** Kibana
  * **Containerization:** Docker & Docker Compose

-----

## System Architecture

The entire workflow is a data pipeline that moves log data from a raw file to a searchable, visual dashboard.

-----

## Prerequisites

Before you begin, ensure you have the following installed on your system:

  * **Docker:** [Get Docker](https://docs.docker.com/get-docker/)
  * **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/)

-----

## Getting Started 🚀

Follow these steps to set up and run the application.

### 1\. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2\. Create the Configuration File

Create a file named `.env` in the root of the project and paste the following content into it. This file provides configuration variables to all the services.

```env
# --- Kafka Topics ---
KAFKA_RAW_LOGS_TOPIC=raw_ipdr_logs
KAFKA_PROCESSED_TOPIC=processed_ipdr_connections

# --- Service Hostnames (match docker-compose service names) ---
KAFKA_HOST=kafka
KAFKA_PORT=29092
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200

# --- Log file path for the producer ---
LOG_FILE_PATH=/data/dummy_logs.json
```

### 3\. Create Sample Data

The `producer` service needs some log data to process.

1.  Create a new directory named `data` in the project root:
    ```bash
    mkdir data
    ```
2.  Create a file inside it named `dummy_logs.json`:
    ```bash
    touch data/dummy_logs.json
    ```
3.  Add a few sample JSON log entries to `data/dummy_logs.json`. **Each JSON object must be on its own line.**
    ```json
    {"timestamp": "2025-08-27T10:00:00Z", "source_ip": "192.168.1.10", "destination_ip": "8.8.8.8", "source_port": 54321, "destination_port": 53, "protocol": "UDP"}
    {"timestamp": "2025-08-27T10:00:01Z", "source_ip": "10.0.0.5", "destination_ip": "1.1.1.1", "source_port": 12345, "destination_port": 443, "protocol": "TCP"}
    {"timestamp": "2025-08-27T10:00:02Z", "user_id": "user-A", "b_party_number": "9876543210", "imei": "123456789012345"}
    ```

-----

## Running the Application

### Start the Pipeline

Run the following command from the project's root directory. This will build the custom Python images and start all the services.

```bash
docker-compose up --build
```

You'll see logs from all the services. The `producer` will send the data and exit, while the other services will continue running.

### Stop the Pipeline

To stop all the running containers, press `Ctrl + C` in the terminal, and then run:

```bash
docker-compose down
```

-----

## Viewing the Results in Kibana 📊

After starting the application, allow a minute for Kibana to initialize.

1.  **Open Kibana:** Navigate to **`http://localhost:5601`** in your web browser.

2.  **Create a Data View:** This tells Kibana which data to look at.

      * Click the menu icon (☰) in the top-left and go to **Stack Management** \> **Data Views**.
      * Click **Create data view**.
      * For the **Index pattern**, type `ipdr_connections`.
      * Click **Save data view to Kibana**.

3.  **Explore Your Data:**

      * Click the main menu icon (☰) again and navigate to **Discover**.
      * You should now see your processed log data, ready to be searched and visualized\!

-----

## Project Structure

  * **/producer**: The Python service that reads log files and sends them to the `raw_ipdr_logs` Kafka topic.
  * **/processor**: The Python service that consumes from `raw_ipdr_logs`, performs analysis (e.g., A-party/B-party mapping), and sends the processed data to the `processed_ipdr_connections` topic.
  * **/consumer**: The Python service that consumes from `processed_ipdr_connections` and indexes the final, clean data into Elasticsearch.
  * **docker-compose.yml**: Defines and orchestrates all the services in the application.

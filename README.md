# IPDR FlowAnalyzer 🚀

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: Active](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Apache Kafka](https://img.shields.io/badge/Apache-Kafka-black.svg)
![Apache Flink](https://img.shields.io/badge/Apache-Flink-orange.svg)

A real-time analytics tool for law enforcement to detect suspicious patterns in massive IPDR logs using Kafka and Flink. Developed for a cybersecurity hackathon to aid in digital forensic investigations.

---

## 📖 About The Project

In digital forensics, investigators often face the monumental task of sifting through millions of Internet Protocol Detail Record (IPDR) logs to find evidence. This process is manual, time-consuming, and prone to error.

**IPDR FlowAnalyzer** was built to solve this problem. It is an intelligent, real-time data processing pipeline that ingests raw IPDR logs and automatically maps communication flows between an initiator (**A-Party**) and a recipient (**B-Party**). By identifying connections and flagging anomalies in real-time, our tool provides law enforcement with actionable intelligence, significantly reducing investigation time and increasing the efficiency of digital forensic support by over 30%.

### Key Features

* **Real-Time Log Ingestion:** Ingests high-volume IPDR streams using Apache Kafka without data loss.
* **A-Party to B-Party Mapping:** Intelligently parses complex logs to identify and map initiator vs. recipient communications.
* **Automated Anomaly Detection:** Utilizes Apache Flink for complex event processing to flag suspicious patterns, such as connections to known malicious IPs or unusual data transfer volumes.
* **Interactive Visualization:** A user-friendly dashboard featuring:
    * **Geographical Map View:** To visualize the physical locations of communicating parties.
    * **Graph-Based Network View:** To explore relationships and connections between different entities.
* **Advanced Query & Search:** A powerful search interface for investigators to filter and query specific sessions, IPs, or timeframes.
* **Data Normalization:** Handles various IPDR formats by normalizing them into a unified schema for consistent analysis.

---

## 🏛️ Architecture

The system is designed as a distributed, scalable pipeline to handle massive data loads.
<img width="4020" height="4005" alt="architecture" src="https://github.com/user-attachments/assets/c53e246a-cd1a-4cb5-8d60-e66eeee98c3e" />

---

## 🛠️ Tech Stack

This project leverages a modern, high-performance technology stack for real-time data processing and analysis.

| Component           | Technology                                                                                                  |
| ------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Data Streaming** | ![Apache Kafka](https://img.shields.io/badge/Apache-Kafka-black.svg)                                        |
| **Stream Processing** | ![Apache Flink](https://img.shields.io/badge/Apache-Flink-orange.svg)                                     |
| **Backend & Logic** | ![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)                                                |
| **Frontend** | ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)           |
| **Database** | ![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white) / ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) |
| **Containerization** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)       |

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Docker and Docker Compose
* Python 3.9+
* Node.js and npm (for the frontend)

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your_username/ipdr-flowanalyzer.git](https://github.com/your_username/ipdr-flowanalyzer.git)
    cd ipdr-flowanalyzer
    ```

2.  **Set up environment variables:**
    * Create a `.env` file from the `env.example`.
    * Fill in the necessary configuration details.

3.  **Launch services with Docker Compose:**
    * This will start Kafka, Flink, and the required databases.
    ```sh
    docker-compose up -d
    ```

4.  **Set up the Backend:**
    ```sh
    cd backend
    pip install -r requirements.txt
    python app.py
    ```

5.  **Set up the Frontend:**
    ```sh
    cd frontend
    npm install
    npm start
    ```

---

## 📈 Usage

Once all services are running:

1.  **Open the application:** Navigate to `http://localhost:3000` in your browser.
2.  **Feed data into Kafka:** Use the provided Python scripts in the `/scripts` directory to simulate an IPDR log stream.
    ```sh
    python scripts/produce_logs.py --file data/sample_ipdr.csv
    ```
3.  **View the Dashboard:** Watch as the dashboard populates with real-time connections, and see anomalies being flagged as they are detected by the Flink job.

![WhatsApp Image 2025-09-01 at 20 27 04](https://github.com/user-attachments/assets/791298b6-d061-4238-833b-e05174675780)


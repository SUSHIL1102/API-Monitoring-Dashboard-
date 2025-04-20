API Monitoring Dashboard Project
Overview
This project implements a comprehensive API monitoring system using Docker, Kafka, Prometheus, Loki, and Grafana. It tracks API request rates, error rates, average response times, recent errors, and log volume, visualized through a Grafana dashboard. The system is designed to simulate API traffic, process it via Kafka, and monitor it with real-time metrics and logs.
Features

Simulates API requests to endpoints (/products, /users, /orders, /invalid).
Publishes metrics to Kafka topics (requests, response_times, errors).
Collects metrics via Prometheus Pushgateway and logs via Loki.
Visualizes data in Grafana with panels for:
Request Rate
Error Rate
Average Response Time
Recent Errors (Loki)
Log Volume (Loki)


Includes basic monitoring with alert configuration.

Prerequisites

Docker and Docker Compose
Basic understanding of Kafka, Prometheus, Loki, and Grafana

Installation

Clone the repository:
git clone <repository-url>
cd <repository-directory>


Start the services using Docker Compose:
docker-compose up -d --build


Clear State (optional, to reset the environment), do this if the kafka container is failing to start:
docker-compose down -v
docker volume prune -f


Verify Containers:
docker ps -a


Create Kafka Topics:
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --create --topic requests --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --create --topic errors --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --create --topic response_times --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1


Verify Topics:
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --list --bootstrap-server kafka:9092


Wait for all containers to initialize (Kafka, Prometheus, Loki, Grafana, workload, consumer).




Usage

Access Grafana at http://localhost:3001 (default credentials: admin/admin).
Navigate to the "API Monitoring Dashboard" to view panels.
Run the workload to generate API traffic and observe real-time updates.
Configure alerts in the Error Rate panel for monitoring.

Configuration

Edit docker-compose.yml to adjust ports or resource limits if needed.
Modify workload.py to change API endpoints or traffic patterns.




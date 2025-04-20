# API Monitoring Dashboard Project

API Monitoring Dashboard is a comprehensive monitoring system built with Docker, Kafka, Prometheus, Loki, and Grafana. It tracks API request rates, error rates, average response times, recent errors, and log volume, visualized through a Grafana dashboard. The system simulates API traffic, processes it via Kafka, and monitors it with real-time metrics and logs.

## Installation

Use Docker and Docker Compose to set up the project.

```bash
git clone <repository-url>
cd <repository-directory>
docker-compose up -d --build
```

### Clear State (optional, to reset the environment), do this if the Kafka container is failing to start:

```bash
docker-compose down -v
docker volume prune -f
```

### Verify Containers:

```bash
docker ps -a
```

### Create Kafka Topics:

```bash
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --create --topic requests --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --create --topic errors --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --create --topic response_times --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

### Verify Topics:

```bash
docker exec applicationmonitoringdashboards-kafka-1 kafka-topics --list --bootstrap-server kafka:9092
```

Wait for all containers to initialize (Kafka, Prometheus, Loki, Grafana, workload, consumer).

## Usage

```bash
# Access Grafana
open http://localhost:3001  # Default credentials: admin/admin
```

- Navigate to the "API Monitoring Dashboard" to view panels.
- Run the workload to generate API traffic and observe real-time updates.
- Configure alerts in the Error Rate panel for monitoring.

## Configuration

- Edit `docker-compose.yml` to adjust ports or resource limits if needed.
- Modify `workload.py` to change API endpoints or traffic patterns.


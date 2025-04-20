import json
from confluent_kafka import Consumer, KafkaError
import requests
from prometheus_client import Counter, Histogram, CollectorRegistry, push_to_gateway
import time
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPICS = ["requests", "errors", "response_times"]
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100")
PROMETHEUS_PUSHGATEWAY_URL = os.getenv("PROMETHEUS_PUSHGATEWAY_URL", "http://pushgateway:9091")

# Prometheus metrics
registry = CollectorRegistry()
request_counter = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["endpoint", "status"],
    registry=registry
)
response_time_histogram = Histogram(
    "api_response_time_seconds",
    "API response time in seconds",
    ["endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, float("inf")],
    registry=registry
)
error_counter = Counter(
    "api_errors_total",
    "Total number of API errors",
    ["endpoint"],
    registry=registry
)

def create_consumer():
    retries = 10
    while retries > 0:
        try:
            consumer = Consumer({
                "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "log-consumer",
                "auto.offset.reset": "earliest"
            })
            consumer.subscribe(KAFKA_TOPICS)
            print(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            return consumer
        except Exception as e:
            print(f"Kafka connection failed: {e}. Retrying ({retries} left)...")
            retries -= 1
            time.sleep(10)
    raise Exception("Failed to connect to Kafka after retries")

def send_to_loki(log, topic):
    try:
        labels = {
            "job": "api_monitoring",
            "topic": topic,
            "endpoint": log.get("endpoint", "unknown")
        }
        log_entry = {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        [str(int(time.time() * 1_000_000_000)), json.dumps(log)]
                    ]
                }
            ]
        }
        response = requests.post(f"{LOKI_URL}/loki/api/v1/push", json=log_entry)
        response.raise_for_status()
        print(f"Sent log to Loki: {log}")
    except Exception as e:
        print(f"Failed to send to Loki: {e}")

def send_to_prometheus(log, topic):
    try:
        endpoint = log.get("endpoint", "unknown")
        status = str(log.get("status", 0))  # Ensure status is string for labels
        response_time = log.get("response_time", 0)

        if topic == "requests":
            request_counter.labels(endpoint=endpoint, status=status).inc()
            response_time_histogram.labels(endpoint=endpoint).observe(response_time)
        elif topic == "errors":
            error_counter.labels(endpoint=endpoint).inc()

        # Push metrics to Pushgateway
        push_to_gateway(
            PROMETHEUS_PUSHGATEWAY_URL,
            job="api_monitoring",
            registry=registry
        )
        print(f"Pushed Prometheus metrics for {topic}: {log}")
    except Exception as e:
        print(f"Failed to push to Prometheus: {e}")

def consume_logs():
    consumer = create_consumer()
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error: {msg.error()}. Continuing...")
                    continue

            try:
                log = json.loads(msg.value().decode("utf-8"))
                topic = msg.topic()
                send_to_loki(log, topic)
                send_to_prometheus(log, topic)
            except Exception as e:
                print(f"Failed to process message: {e}")
    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    print("Consumer starting...")
    consume_logs()
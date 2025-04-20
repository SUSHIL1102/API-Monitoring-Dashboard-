import requests
import time
import json
from confluent_kafka import Producer
import random
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
API_URL = "http://api:3000"
ENDPOINTS = ["/users", "/products", "/orders", "/invalid"]  # Added invalid endpoint

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()}")

def produce_log(topic, log):
    try:
        producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
        producer.produce(topic, json.dumps(log).encode("utf-8"), callback=delivery_report)
        producer.flush()
    except Exception as e:
        print(f"Failed to produce to {topic}: {e}")

def simulate_requests():
    while True:
        endpoint = random.choice(ENDPOINTS)  # Randomly select, including /invalid
        start_time = time.time()
        try:
            response = requests.get(f"{API_URL}{endpoint}")
            response_time = time.time() - start_time
            log = {
                "timestamp": time.time(),
                "endpoint": endpoint,
                "status": response.status_code,
                "response_time": response_time
            }
            produce_log("requests", log)
            if not response.ok:  # e.g., 404 for /invalid
                error_log = {**log, "error": response.text}
                produce_log("errors", error_log)
            produce_log("response_times", log)
        except Exception as e:
            print(f"Request failed: {e}")
            error_log = {
                "timestamp": time.time(),
                "endpoint": endpoint,
                "status": 0,
                "response_time": 0,
                "error": str(e)
            }
            produce_log("errors", error_log)
        time.sleep(1)

if __name__ == "__main__":
    print("Workload starting...")
    simulate_requests()
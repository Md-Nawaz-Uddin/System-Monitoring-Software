#!/usr/bin/env python3

import platform
import psutil
import requests
import json
import time
import uuid
import socket

SERVER_URL = "https://your-server-ip/api/report"  # Replace with your actual server IP
AUTH_TOKEN = "your-agent-secret"  # Optional: Not implemented yet in backend

def collect_data():
    return {
        "hostname": socket.gethostname(),
        "uuid": str(uuid.uuid4()),
        "os": platform.platform(),
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "user": platform.node()
    }

def send_data():
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    try:
        data = collect_data()
        response = requests.post(SERVER_URL, json=data, headers=headers, timeout=5)
        print(f"[Agent] Sent data: {response.status_code}")
    except Exception as e:
        print("Error sending data:", e)

if __name__ == "__main__":
    while True:
        send_data()
        time.sleep(300)  # 5 minutes

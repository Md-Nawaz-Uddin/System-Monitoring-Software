#!/usr/bin/env python3
import platform, psutil, requests, json, time, uuid, socket
SERVER_URL = "https://your-server-ip/api/report"
AUTH_TOKEN = "your-agent-secret"
def collect_data():
return {
"hostname": socket.gethostname(),
"uuid": str(uuid.uuid4()),
"os": platform.platform(),
"cpu": psutil.cpu_percent(),
"ram": psutil.virtual_memory().percent,
"disk": psutil.disk_usage('/').percent,
"user": platform.node()
}
1def send_data():
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
try:
requests.post(SERVER_URL, json=collect_data(), headers=headers,
timeout=5)
except Exception as e:
print("Error:", e)
if __name__ == "__main__":
while True:
send_data()
time.sleep(300)

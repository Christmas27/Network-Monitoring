# Updated monitor.py
import requests
import sqlite3
from dotenv import load_dotenv
import os
import json

load_dotenv()
DNAC_HOST = os.getenv("DNAC_HOST")
DNAC_USER = os.getenv("DNAC_USER")
DNAC_PASS = os.getenv("DNAC_PASS")

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# 1. Get Token
auth_url = f"{DNAC_HOST}/dna/system/api/v1/auth/token"
auth_response = requests.post(auth_url, auth=(DNAC_USER, DNAC_PASS), verify=False)
token = auth_response.json()["Token"]

# 2. Fetch DEVICE health (correct endpoint)
devices_url = f"{DNAC_HOST}/dna/intent/api/v1/device-health"  # Changed from network-health
headers = {"X-Auth-Token": token}
response = requests.get(devices_url, headers=headers, verify=False)

# Debug: Print raw response
print(json.dumps(response.json(), indent=2))

# 3. Store in SQLite
conn = sqlite3.connect("network.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        name TEXT,
        cpu TEXT,
        memory TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")  # Using proper SQL comments

# Process devices
devices = response.json()["response"]
for device in devices:
    name = device.get("name", "N/A")
    cpu = str(device.get("cpuUtilization", "N/A"))
    memory = str(device.get("memoryUtilization", "N/A"))
    print(f"Device: {name}, CPU: {cpu}%, Memory: {memory}%")
    cursor.execute(
        "INSERT INTO devices (name, cpu, memory) VALUES (?, ?, ?)",
        (name, cpu, memory)
    )

conn.commit()
conn.close()
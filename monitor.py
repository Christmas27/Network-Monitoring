# Updated monitor.py (with debug steps)
import requests
import sqlite3
from dotenv import load_dotenv
import os
import json  # Add this

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

# 2. Fetch Devices
devices_url = f"{DNAC_HOST}/dna/intent/api/v1/network-health"
headers = {"X-Auth-Token": token}
response = requests.get(devices_url, headers=headers, verify=False)

# Debug: Print raw response
print(json.dumps(response.json(), indent=2))  # Inspect this output!

devices = response.json()["response"]

# 3. Store in SQLite
conn = sqlite3.connect("network.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        name TEXT,
        cpu TEXT,  # Changed to TEXT if values are "45%"
        memory TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Use this to handle potential field name changes
for device in devices:
    name = device.get("name") or device.get("hostname") or "N/A"  # Covers both old/new keys
    cpu = device.get("cpu") or device.get("cpuUtilization") or "N/A"
    memory = device.get("memory") or device.get("memoryUtilization") or "N/A"
    print(f"Device: {name}, CPU: {cpu}, Memory: {memory}")

conn.commit()
conn.close()
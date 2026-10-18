#!/usr/bin/env python3
"""
NemoClaw Laptop Edge Worker Daemon
Runs locally on your laptop / workstation. Connects to the Home Server over Tailscale.
- Reports local hardware telemetry to local personal vault
- Executes workstation-local tasks (e.g., git status, local files, local models)
"""

import os
import sys
import time
import json
import socket
import platform
import subprocess
import httpx

HOME_SERVER_URL = os.getenv("HOME_SERVER_URL", "http://localhost:8003")
NODE_ID = os.getenv("NODE_ID", socket.gethostname())
NODE_ROLE = "laptop"

def get_tailscale_ip() -> str:
    try:
        res = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "127.0.0.1"

def collect_telemetry() -> dict:
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = int(psutil.virtual_memory().used / (1024 * 1024))
    disk = round(psutil.disk_usage("/").free / (1024 * 1024 * 1024), 2)
    battery = None
    if hasattr(psutil, "sensors_battery"):
        b = psutil.sensors_battery()
        if b:
            battery = int(b.percent)

    return {
        "node_id": NODE_ID,
        "node_role": NODE_ROLE,
        "cpu_percent": cpu,
        "ram_used_mb": ram,
        "disk_free_gb": disk,
        "network_mode": "tailscale",
        "battery_level": battery,
        "tailscale_ip": get_tailscale_ip()
    }

def main():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from banner import print_banner
        print_banner(node_role="Laptop Edge Worker", tailscale_ip=get_tailscale_ip())
    except Exception:
        print("🦁 NemoClaw Laptop Edge Daemon Online")

    while True:
        try:
            # Report telemetry every 60s
            telemetry = collect_telemetry()
            with httpx.Client(timeout=5.0) as client:
                client.post(f"{HOME_SERVER_URL}/telemetry", json=telemetry)
            print(f"[{time.strftime('%X')}] Heartbeat sent: CPU {telemetry['cpu_percent']}%, RAM {telemetry['ram_used_mb']}MB")
        except Exception as e:
            print(f"[{time.strftime('%X')}] Server sync notice: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()

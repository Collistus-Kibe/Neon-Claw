import schedule
import time
import subprocess
import socket
import os

MODE_FILE = "/shared/neon_mode.txt"
TEMP_FILE = "/shared/neon_mode.tmp"

def ping_network() -> bool:
    # 1. Try socket connect to DNS port 53 (Reliable without raw socket privileges)
    try:
        s = socket.create_connection(("1.1.1.1", 53), timeout=1.5)
        s.close()
        return True
    except Exception:
        pass

    # 2. Fallback to ICMP ping
    try:
        param = '-n' if os.name == 'nt' else '-c'
        command = ['ping', param, '1', '8.8.8.8']
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False

def check_mode():
    is_live = ping_network()
    mode = "live" if is_live else "dark"
    
    # Check for Tailscale mesh presence
    try:
        ts = subprocess.run(["tailscale", "status"], capture_output=True, text=True, timeout=2)
        if ts.returncode == 0 and "Logged in" in ts.stdout:
            mode += "+tailscale"
    except Exception:
        pass

    try:
        os.makedirs(os.path.dirname(MODE_FILE), exist_ok=True)
        # Atomic Write to prevent race conditions during bot read
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(mode)
        os.replace(TEMP_FILE, MODE_FILE)
        print(f"[NeonShell] Network mode updated: {mode}")
    except Exception as e:
        print(f"[NeonShell] Failed to write mode file: {e}")

def run():
    print("🦁 NeonShell Network & Security Monitor started.")
    check_mode()
    schedule.every(30).seconds.do(check_mode)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run()

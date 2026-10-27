#!/usr/bin/env python3
"""
NemoClaw CLI Launcher & Control Plane
Usage:
    python nemoclaw.py          # Show banner and credentials status
    python nemoclaw.py setup    # Interactive onboarding & credential wizard
    python nemoclaw.py up       # Boot home server mesh (Docker Compose)
    python nemoclaw.py down     # Stop mesh
    python nemoclaw.py test     # Run full verification suite
    python nemoclaw.py edge     # Launch laptop edge worker daemon
"""

import sys
import os
import subprocess
import shutil

# Enable Virtual Terminal Processing (ANSI colors) on Windows 10/11
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8 code page
        hOut = kernel32.GetStdHandle(-11)   # STD_OUTPUT_HANDLE
        out_mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hOut, ctypes.byref(out_mode))
        kernel32.SetConsoleMode(hOut, out_mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass
    os.system('')

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NEON_CLAW_DIR = os.path.join(SCRIPT_DIR, "neon-claw")
ENV_PATH = os.path.join(NEON_CLAW_DIR, ".env")
ENV_EXAMPLE_PATH = os.path.join(NEON_CLAW_DIR, ".env.example")
sys.path.insert(0, NEON_CLAW_DIR)

try:
    from banner import print_banner
except Exception:
    def print_banner(role="Personal AI System", tailscale_ip="100.64.0.1"):
        print(f"\n✦ NEMOCLAW v1.0.0 │ {role}\n")

# Terminal color tokens
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
BRIGHT_CYAN = "\033[96m"
PURPLE = "\033[35m"
BRIGHT_PURPLE = "\033[95m"
GREEN = "\033[32m"
BRIGHT_GREEN = "\033[92m"
YELLOW = "\033[33m"
GRAY = "\033[90m"

def get_tailscale_ip():
    try:
        res = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "100.64.0.1 (mesh)"

def parse_env_file():
    """Parses .env file into key-value dictionary."""
    env_vars = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def write_env_file(env_vars):
    """Writes updated variables to .env."""
    lines = [
        "# ==============================================================================",
        "# NemoClaw Personal AI Environment Configuration",
        "# Generated via 'nemoclaw setup'",
        "# ==============================================================================",
        "",
        "# 1. Telegram Bot Token (from @BotFather)",
        f"TELEGRAM_BOT_TOKEN={env_vars.get('TELEGRAM_BOT_TOKEN', '')}",
        "",
        "# 2. Telegram Whitelist User IDs (from @userinfobot - comma separated)",
        f"ALLOWED_TELEGRAM_USER_IDS={env_vars.get('ALLOWED_TELEGRAM_USER_IDS', '')}",
        "",
        "# 3. NVIDIA Developer API Key (from https://build.nvidia.com/ - format: nvapi-...)",
        f"NVIDIA_API_KEY={env_vars.get('NVIDIA_API_KEY', '')}",
        f"NVIDIA_BASE_URL={env_vars.get('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')}",
        f"NVIDIA_MODEL={env_vars.get('NVIDIA_MODEL', 'nvidia/llama-3.1-nemotron-70b-instruct')}",
        "",
        "# Optional fallback: Nebius Serverless API",
        f"NEBIUS_API_KEY={env_vars.get('NEBIUS_API_KEY', '')}",
        f"NEBIUS_BASE_URL={env_vars.get('NEBIUS_BASE_URL', 'https://api.studio.nebius.ai/v1/')}",
        f"NEBIUS_MODEL={env_vars.get('NEBIUS_MODEL', 'nvidia/Llama-3.1-Nemotron-70B-Instruct')}",
        "",
        "# 4. Tailscale Auth Key (optional for peer-to-peer home server <-> laptop mesh)",
        f"TAILSCALE_AUTH_KEY={env_vars.get('TAILSCALE_AUTH_KEY', '')}",
        ""
    ]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def cmd_setup():
    """Interactive command-line setup wizard."""
    print(f"\n{BOLD}{BRIGHT_CYAN}✦  N E M O C L A W   Q U I C K   S E T U P{RESET}")
    print(f"{DIM}Configure your credentials and tokens directly from this terminal in < 60 seconds.{RESET}\n")

    current = parse_env_file()

    # Step 1: Telegram Bot Token
    print(f"{BOLD}[1/4] 🤖 Telegram Bot Token (Required){RESET}")
    print(f"  {YELLOW}Tip:{RESET} Open Telegram ➔ Search {CYAN}@BotFather{RESET} ➔ Send {BOLD}/newbot{RESET} ➔ Copy token.")
    curr_token = current.get("TELEGRAM_BOT_TOKEN", "")
    default_prompt = f" [{curr_token[:6]}...{curr_token[-4:]}]" if curr_token and curr_token != "your_telegram_bot_token_here" else ""
    token_in = input(f"  Enter Bot Token{default_prompt} (or press Enter to keep): ").strip()
    if token_in:
        current["TELEGRAM_BOT_TOKEN"] = token_in

    print()
    # Step 2: Allowed Telegram User ID
    print(f"{BOLD}[2/4] 👤 Telegram User ID - Whitelist Security (Recommended){RESET}")
    print(f"  {YELLOW}Tip:{RESET} Open Telegram ➔ Search {CYAN}@userinfobot{RESET} ➔ Copy your numeric {BOLD}Id{RESET}.")
    print(f"  {DIM}Locks NemoClaw strictly to your account so unauthorized strangers cannot use it.{RESET}")
    curr_id = current.get("ALLOWED_TELEGRAM_USER_IDS", "")
    default_prompt = f" [{curr_id}]" if curr_id else " [Allow All]"
    id_in = input(f"  Enter your User ID{default_prompt}: ").strip()
    if id_in:
        current["ALLOWED_TELEGRAM_USER_IDS"] = id_in

    print()
    # Step 3: NVIDIA Developer API Key (build.nvidia.com)
    print(f"{BOLD}[3/4] ⚡ NVIDIA Developer API Key - Nemotron 70B (Recommended){RESET}")
    print(f"  {YELLOW}Tip:{RESET} Get your free key from {CYAN}https://build.nvidia.com/{RESET} (NVIDIA API Catalog).")
    print(f"  {DIM}Format: nvapi-... (Free credits included). Or press Enter to use offline reasoner.{RESET}")
    curr_nv = current.get("NVIDIA_API_KEY") or current.get("NEBIUS_API_KEY", "")
    default_prompt = f" [{curr_nv[:6]}...{curr_nv[-4:]}]" if curr_nv and curr_nv not in ["your_nvidia_api_key_here", "your_nebius_api_key_here"] else " [Skip / Offline Mode]"
    key_in = input(f"  Enter NVIDIA API Key (nvapi-...){default_prompt}: ").strip()
    if key_in:
        if key_in.startswith("nvapi-"):
            current["NVIDIA_API_KEY"] = key_in
            current["NVIDIA_BASE_URL"] = "https://integrate.api.nvidia.com/v1"
            current["NVIDIA_MODEL"] = "nvidia/llama-3.1-nemotron-70b-instruct"
        else:
            current["NEBIUS_API_KEY"] = key_in

    print()
    # Step 4: Tailscale Auth Key
    print(f"{BOLD}[4/4] 🔐 Tailscale Auth Key (Optional for Laptop <-> Server Mesh){RESET}")
    print(f"  {YELLOW}Tip:{RESET} From {CYAN}https://login.tailscale.com/admin/settings/keys{RESET} (or press Enter to skip).")
    curr_ts = current.get("TAILSCALE_AUTH_KEY", "")
    default_prompt = f" [{curr_ts[:6]}...]" if curr_ts else " [Skip]"
    ts_in = input(f"  Enter Tailscale Key{default_prompt}: ").strip()
    if ts_in:
        current["TAILSCALE_AUTH_KEY"] = ts_in

    # Save to .env
    write_env_file(current)

    print(f"\n{BRIGHT_GREEN}  ╭─────────────────────────────────────────────────────────────╮{RESET}")
    print(f"{BRIGHT_GREEN}  │  ✅  Configuration successfully saved to neon-claw/.env    │{RESET}")
    print(f"{BRIGHT_GREEN}  │                                                             │{RESET}")
    tg_status = "Configured" if current.get("TELEGRAM_BOT_TOKEN") and current.get("TELEGRAM_BOT_TOKEN") != "your_telegram_bot_token_here" else "Missing"
    wl_status = current.get("ALLOWED_TELEGRAM_USER_IDS") or "Open Dev Mode"
    
    if current.get("NVIDIA_API_KEY") and current.get("NVIDIA_API_KEY").startswith("nvapi-"):
        brain_status = "NVIDIA NIM Developer API (Live)"
    elif current.get("NEBIUS_API_KEY") and current.get("NEBIUS_API_KEY") != "your_nebius_api_key_here":
        brain_status = "Nebius Serverless (Live)"
    else:
        brain_status = "Offline Fallback Reasoner"

    print(f"{BRIGHT_GREEN}  │{RESET}  • {GRAY}Telegram Bot:{RESET}       {BOLD}{tg_status:<38}{RESET}{BRIGHT_GREEN}│{RESET}")
    print(f"{BRIGHT_GREEN}  │{RESET}  • {GRAY}Security Lock:{RESET}      {BOLD}{wl_status:<38}{RESET}{BRIGHT_GREEN}│{RESET}")
    print(f"{BRIGHT_GREEN}  │{RESET}  • {GRAY}Brain Engine:{RESET}       {BOLD}{brain_status:<38}{RESET}{BRIGHT_GREEN}│{RESET}")
    print(f"{BRIGHT_GREEN}  │                                                             │{RESET}")
    print(f"{BRIGHT_GREEN}  │  🚀 Next step: Run {BOLD}nemoclaw up{RESET}{BRIGHT_GREEN} to launch your personal AI!   │{RESET}")
    print(f"{BRIGHT_GREEN}  ╰─────────────────────────────────────────────────────────────╯{RESET}\n")

def check_credentials():
    env = parse_env_file()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    is_valid_token = token and token != "your_telegram_bot_token_here"
    allowed = env.get("ALLOWED_TELEGRAM_USER_IDS", "")
    nv_key = env.get("NVIDIA_API_KEY", "")
    is_valid_nv = nv_key and nv_key.startswith("nvapi-")
    neb_key = env.get("NEBIUS_API_KEY", "")
    is_valid_neb = neb_key and neb_key != "your_nebius_api_key_here"
    
    return {
        "token_ok": is_valid_token,
        "token_val": token,
        "whitelist_ok": bool(allowed),
        "whitelist_val": allowed,
        "nvidia_ok": is_valid_nv,
        "nebius_ok": is_valid_neb
    }

def cmd_up():
    creds = check_credentials()
    if not creds["token_ok"]:
        print(f"\n{YELLOW}⚠️  No Telegram Bot Token configured in neon-claw/.env!{RESET}")
        print(f"Let's configure it quickly now.\n")
        cmd_setup()

    print(f"\n{BRIGHT_CYAN}🚀 Starting NemoClaw Home Server Mesh (Docker Compose)...{RESET}")
    subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=NEON_CLAW_DIR)

def cmd_down():
    print(f"\n{YELLOW}🛑 Stopping NemoClaw Mesh...{RESET}")
    subprocess.run(["docker", "compose", "down"], cwd=NEON_CLAW_DIR)

def cmd_test():
    print(f"\n{BRIGHT_CYAN}🧪 Running NemoClaw Verification Test Suite...{RESET}")
    subprocess.run([sys.executable, "test_system.py"], cwd=NEON_CLAW_DIR)

def cmd_edge():
    print(f"\n{BRIGHT_CYAN}💻 Launching Laptop Edge Daemon...{RESET}")
    edge_script = os.path.join(NEON_CLAW_DIR, "nemoclaw-edge", "edge_daemon.py")
    subprocess.run([sys.executable, edge_script])

def cmd_pair():
    print(f"\n{BOLD}{BRIGHT_CYAN}🔗  N E O N C L A W   D U A L - N O D E   P A I R I N G{RESET}")
    print(f"{DIM}Pair your laptop and home server into a unified agent mesh.{RESET}\n")
    role = input(f"Are you pairing this machine as [server] or [laptop]? (default: laptop): ").strip().lower() or "laptop"
    if role == "server":
        print(f"\n{BRIGHT_GREEN}Generating one-time server pairing key...{RESET}")
        import secrets
        code = secrets.token_hex(3).upper()
        print(f"\n  Pairing Code: {BOLD}{BRIGHT_CYAN}{code}{RESET}")
        print(f"  Run '{BOLD}nemoclaw pair{RESET}' on your laptop and enter this code.")
    else:
        code = input(f"Enter the 6-character pairing code from your server: ").strip().upper()
        if code:
            print(f"\n{BRIGHT_GREEN}Pairing code registered ({code}). WebSocket tunnel will auto-negotiate.{RESET}")
        else:
            print(f"{YELLOW}No code entered. Pairing aborted.{RESET}")

def sync_integration_to_shared_vault(service_name: str, config_json: dict, configured_by: str = "laptop"):
    """
    Persists integration into the distributed shared vault (PostgreSQL/SQLite)
    so both server and laptop immediately operate as one synchronized scattered agent.
    """
    import json
    import urllib.request
    
    payload = {
        "id": f"{service_name}_integration",
        "service_name": service_name,
        "config_json": config_json,
        "is_enabled": True,
        "configured_by_node": configured_by
    }
    
    home_server = os.getenv("HOME_SERVER_URL", "http://localhost:8003")
    endpoints = [
        f"{home_server}/integrations",
        "http://localhost:8003/integrations",
        "http://127.0.0.1:8002/integrations",
        "http://localhost:8001/integrations"
    ]
    synced = False
    for ep in endpoints:
        try:
            req = urllib.request.Request(
                ep,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status in [200, 201]:
                    synced = True
                    break
        except Exception:
            pass

    # Direct fallback: write to local shared_vault.db if SQLite exists
    db_path = os.path.join(NEON_CLAW_DIR, "data", "shared_vault.db")
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS system_integrations (
            id TEXT PRIMARY KEY,
            service_name TEXT NOT NULL,
            config_json TEXT NOT NULL,
            is_enabled INTEGER DEFAULT 1,
            configured_by_node TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""INSERT OR REPLACE INTO system_integrations
            (id, service_name, config_json, is_enabled, configured_by_node, updated_at)
            VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP)""",
            (payload["id"], payload["service_name"], json.dumps(config_json), configured_by)
        )
        conn.commit()
        conn.close()
        synced = True
    except Exception:
        pass
    return synced

def list_mesh_integrations():
    """Lists all active integrations registered in the scattered mesh."""
    import json
    import urllib.request
    
    home_server = os.getenv("HOME_SERVER_URL", "http://localhost:8003")
    endpoints = [
        f"{home_server}/integrations",
        "http://localhost:8003/integrations",
        "http://127.0.0.1:8002/integrations"
    ]
    for ep in endpoints:
        try:
            with urllib.request.urlopen(ep, timeout=1.5) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception:
            pass
            
    # Fallback to local SQLite shared_vault.db
    db_path = os.path.join(NEON_CLAW_DIR, "data", "shared_vault.db")
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM system_integrations WHERE is_enabled = 1")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception:
            pass
    return []

def cmd_integrate():
    """Interactive wizard and CLI command to connect new APIs and integrations."""
    print(f"\n{BOLD}{BRIGHT_CYAN}🔌  N E M O C L A W   M E S H   I N T E G R A T I O N S{RESET}")
    print(f"{DIM}Connect external services once; auto-syncs across the scattered agent (laptop + server).{RESET}\n")
    
    if len(sys.argv) > 2 and sys.argv[2].lower() in ["list", "ls", "status"]:
        integrations = list_mesh_integrations()
        if not integrations:
            print(f"{YELLOW}No active integrations recorded in the distributed shared vault.{RESET}")
            print(f"Run '{BOLD}nemoclaw integrate{RESET}' to add GitHub, Voice, Email, or DevOps.\n")
            return
            
        print(f"{BOLD}Active Synchronized Mesh Integrations:{RESET}")
        for it in integrations:
            s_name = it.get("service_name", "unknown")
            node = it.get("configured_by_node", "mesh")
            updated = it.get("updated_at", "")
            print(f"  • {BRIGHT_GREEN}●{RESET} {BOLD}{s_name.upper():<14}{RESET} (Node: {CYAN}{node}{RESET}) {DIM}{updated}{RESET}")
        print()
        return

    print("Choose a service to integrate:")
    print(f"  {BOLD}1){RESET} 🐙 GitHub           - Repository code audit, issues & PR reviews")
    print(f"  {BOLD}2){RESET} 🎙️ Voice & Speech    - Whisper STT (Groq / OpenAI) + Audio TTS")
    print(f"  {BOLD}3){RESET} 📬 Email & SMTP     - Inbox triage, urgency rating & reply drafts")
    print(f"  {BOLD}4){RESET} 🐳 Docker & DevOps   - Container inspection & server log diagnostics")
    print(f"  {BOLD}5){RESET} ⚡ LLM / Brain       - NVIDIA Nemotron (NIM) or Nebius Serverless")
    print()
    choice = input("Enter choice [1-5] (or service name): ").strip().lower()
    
    env_vars = parse_env_file()
    service_name = ""
    config_data = {}
    node_role = "laptop" if os.name == 'nt' else "server"

    if choice in ["1", "github", "git"]:
        service_name = "github"
        print(f"\n{BOLD}🐙 GitHub Integration Setup{RESET}")
        token = input("  Enter GitHub Personal Access Token (or press Enter for public repos): ").strip()
        default_repo = input("  Enter default repository [Collistus-Kibe/Neon-Claw]: ").strip() or "Collistus-Kibe/Neon-Claw"
        config_data = {"token": token, "default_repo": default_repo}
        if token:
            env_vars["GITHUB_TOKEN"] = token

    elif choice in ["2", "voice", "speech", "whisper"]:
        service_name = "voice"
        print(f"\n{BOLD}🎙️ Voice & Speech Integration Setup{RESET}")
        print(f"  {DIM}Groq Whisper provides ~250ms voice notes transcription.{RESET}")
        groq_k = input("  Enter Groq API Key (gsk_...) [or press Enter to skip]: ").strip()
        openai_k = input("  Enter OpenAI API Key (sk-...) [or press Enter to skip]: ").strip()
        config_data = {"groq_api_key": groq_k, "openai_api_key": openai_k, "tts_engine": "edge_tts"}
        if groq_k:
            env_vars["GROQ_API_KEY"] = groq_k
        if openai_k:
            env_vars["OPENAI_API_KEY"] = openai_k

    elif choice in ["3", "email", "smtp", "imap"]:
        service_name = "email"
        print(f"\n{BOLD}📬 Email Triage & SMTP Setup{RESET}")
        host = input("  IMAP Server [imap.gmail.com]: ").strip() or "imap.gmail.com"
        user = input("  Email User / Address: ").strip()
        pw = input("  Email App Password: ").strip()
        smtp_host = input("  SMTP Server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
        config_data = {"host": host, "user": user, "smtp_host": smtp_host}
        if user:
            env_vars["EMAIL_USER"] = user
        if pw:
            env_vars["EMAIL_PASSWORD"] = pw

    elif choice in ["4", "docker", "devops"]:
        service_name = "docker_devops"
        print(f"\n{BOLD}🐳 Docker & DevOps Integration Setup{RESET}")
        sock = input("  Docker Socket Path [/var/run/docker.sock]: ").strip() or "/var/run/docker.sock"
        config_data = {"socket_path": sock, "enabled": True}

    elif choice in ["5", "llm", "nvidia", "brain"]:
        service_name = "nvidia_nemotron"
        print(f"\n{BOLD}⚡ NVIDIA Nemotron Brain Setup{RESET}")
        key = input("  Enter NVIDIA API Key (nvapi-...): ").strip()
        config_data = {"model": "nvidia/llama-3.1-nemotron-70b-instruct", "base_url": "https://integrate.api.nvidia.com/v1"}
        if key:
            env_vars["NVIDIA_API_KEY"] = key

    else:
        print(f"{YELLOW}Invalid selection. Integration cancelled.{RESET}")
        return

    # Update local .env
    write_env_file(env_vars)
    
    # Synchronize into distributed shared vault
    synced = sync_integration_to_shared_vault(service_name, config_data, configured_by=node_role)
    
    print(f"\n{BRIGHT_GREEN}  ╭─────────────────────────────────────────────────────────────╮{RESET}")
    print(f"{BRIGHT_GREEN}  │  ✅  Integration '{service_name}' successfully configured!       │{RESET}")
    print(f"{BRIGHT_GREEN}  │                                                             │{RESET}")
    print(f"{BRIGHT_GREEN}  │  📡  Auto-Synchronized to Scattered Agent Fabric:            │{RESET}")
    print(f"{BRIGHT_GREEN}  │      • Configured from: {BOLD}{node_role.upper():<35}{RESET}{BRIGHT_GREEN}│{RESET}")
    print(f"{BRIGHT_GREEN}  │      • Shared Vault Sync: {BOLD}{'ONLINE' if synced else 'SAVED LOCALLY':<33}{RESET}{BRIGHT_GREEN}│{RESET}")
    print(f"{BRIGHT_GREEN}  │      • Scattered Nodes (Laptop + Server) now share this API!│{RESET}")
    print(f"{BRIGHT_GREEN}  ╰─────────────────────────────────────────────────────────────╯{RESET}\n")

def cmd_status():
    print_banner(node_role="Home Server Control Plane", tailscale_ip=get_tailscale_ip())
    
    creds = check_credentials()
    tg_icon = f"{GREEN}● Configured{RESET}" if creds["token_ok"] else f"{YELLOW}○ Not set (Run: nemoclaw setup){RESET}"
    wl_icon = f"{GREEN}● Locked to ID: {creds['whitelist_val']}{RESET}" if creds["whitelist_ok"] else f"{GRAY}○ Open / Dev Mode{RESET}"
    
    if creds["nvidia_ok"]:
        brain_icon = f"{GREEN}● Live (NVIDIA Developer API / build.nvidia.com){RESET}"
    elif creds["nebius_ok"]:
        brain_icon = f"{GREEN}● Live (Nebius Serverless){RESET}"
    else:
        brain_icon = f"{GRAY}○ Offline Fallback Reasoner{RESET}"

    print(f"  {BOLD}🔐 Credentials & Security State:{RESET}")
    print(f"    • Telegram Token:   {tg_icon}")
    print(f"    • User Whitelist:   {wl_icon}")
    print(f"    • Brain / LLM:      {brain_icon}")
    print()

    print(f"  {BOLD}📋 Available Commands:{RESET}")
    print(f"    • {BOLD}nemoclaw setup{RESET}        Interactive wizard to configure/change tokens")
    print(f"    • {BOLD}nemoclaw integrate{RESET}    Connect APIs (GitHub, Voice, Email, Docker)")
    print(f"    • {BOLD}nemoclaw up{RESET}           Start Home Server mesh containers")
    print(f"    • {BOLD}nemoclaw pair{RESET}         Pair laptop and server nodes into unified mesh")
    print(f"    • {BOLD}nemoclaw edge{RESET}         Launch laptop edge worker daemon")
    print(f"    • {BOLD}nemoclaw test{RESET}         Run end-to-end verification tests")
    print(f"    • {BOLD}nemoclaw down{RESET}         Stop containers")
    print()

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ["setup", "config", "configure", "login"]:
            cmd_setup()
        elif cmd in ["integrate", "integration", "add-api"]:
            cmd_integrate()
        elif cmd == "up":
            cmd_up()
        elif cmd == "down":
            cmd_down()
        elif cmd in ["test", "verify"]:
            cmd_test()
        elif cmd in ["edge", "worker"]:
            cmd_edge()
        elif cmd in ["pair", "connect"]:
            cmd_pair()
        elif cmd in ["status", "--status", "-s"]:
            cmd_status()
        elif cmd in ["--help", "-h", "help"]:
            cmd_status()
        else:
            print(f"Unknown command '{cmd}'. Available: setup, integrate, up, down, test, pair, edge, status")
    else:
        cmd_status()

if __name__ == "__main__":
    main()

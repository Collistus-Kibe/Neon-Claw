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
    print(f"    • {BOLD}nemoclaw setup{RESET}    Interactive wizard to configure/change tokens")
    print(f"    • {BOLD}nemoclaw up{RESET}       Start Home Server mesh containers")
    print(f"    • {BOLD}nemoclaw test{RESET}     Run end-to-end verification tests")
    print(f"    • {BOLD}nemoclaw edge{RESET}     Launch laptop edge worker daemon")
    print(f"    • {BOLD}nemoclaw down{RESET}     Stop containers")
    print()

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ["setup", "config", "configure", "login"]:
            cmd_setup()
        elif cmd == "up":
            cmd_up()
        elif cmd == "down":
            cmd_down()
        elif cmd in ["test", "verify"]:
            cmd_test()
        elif cmd in ["edge", "worker"]:
            cmd_edge()
        elif cmd in ["status", "--status", "-s"]:
            cmd_status()
        elif cmd in ["--help", "-h", "help"]:
            cmd_status()
        else:
            print(f"Unknown command '{cmd}'. Available: setup, up, down, test, edge, status")
    else:
        cmd_status()

if __name__ == "__main__":
    main()

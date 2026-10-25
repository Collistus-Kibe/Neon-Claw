"""
NeonClaw Claude-Code Style Terminal Banner v2.0
Provides clean, modern, high-aesthetic startup visuals with ASCII art and live dual-node subsystem indicators.
Automatically enables ANSI colors & UTF-8 on Windows cmd.exe and PowerShell.
"""

import os
import sys
import re
import unicodedata

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
    os.system('')  # Standard fallback to activate VT100 in cmd.exe

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(s: str) -> str:
    return ANSI_ESCAPE.sub('', s)

def get_char_width(ch: str) -> int:
    code = ord(ch)
    if code in (0x200B, 0x200C, 0x200D, 0xFEFF):
        return 0
    if (0x1F300 <= code <= 0x1FAFF) or (0x2600 <= code <= 0x27BF) or (0x2300 <= code <= 0x23FF):
        if ch in ('✦', '│', '─', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼', '╭', '╮', '╯', '╰', '═', '║', '╔', '╗', '╚', '╝', '◄', '►', '•', '●', '○'):
            return 1
        return 2
    ea = unicodedata.east_asian_width(ch)
    if ea in ('W', 'F'):
        return 2
    return 1

def str_width(s: str) -> int:
    plain = strip_ansi(s)
    return sum(get_char_width(c) for c in plain)

def get_banner(
    node_role: str = "Home Server Control Plane",
    tailscale_ip: str = "100.64.0.1",
    server_online: bool = True,
    laptop_online: bool = True
) -> str:
    # ANSI Colors
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

    WIDTH = 74
    BORDER = BRIGHT_PURPLE

    def box_row(text: str) -> str:
        w = str_width(text)
        pad = max(0, WIDTH - w)
        return f"  {BORDER}║{RESET}{text}{' ' * pad}{BORDER}║{RESET}"

    top = f"  {BORDER}╔{'═' * WIDTH}╗{RESET}"
    bot = f"  {BORDER}╚{'═' * WIDTH}╝{RESET}"
    empty = f"  {BORDER}║{' ' * WIDTH}║{RESET}"

    ascii_art = [
        f"  {BRIGHT_CYAN}███╗   ██╗███████╗ ██████╗ ███╗   ██╗ ██████╗██╗      █████╗ ██╗    ██╗{RESET}",
        f"  {BRIGHT_CYAN}████╗  ██║██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔══██╗██║    ██║{RESET}",
        f"  {CYAN}██╔██╗ ██║█████╗  ██║   ██║██╔██╗ ██║██║     ██║     ███████║██║ █╗ ██║{RESET}",
        f"  {PURPLE}██║╚██╗██║██╔══╝  ██║   ██║██║╚██╗██║██║     ██║     ██╔══██║██║███╗██║{RESET}",
        f"  {BRIGHT_PURPLE}██║ ╚████║███████╗╚██████╔╝██║ ╚████║╚██████╗███████╗██║  ██║╚███╔███╔╝{RESET}",
        f"  {BRIGHT_PURPLE}╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ {RESET}",
    ]

    sub_bar = (
        f"  {GRAY}{'─' * WIDTH}{RESET}\n"
        f"  {DIM} v2.0.0  │  Open-Source Personal AI  │  Dual-Node: Laptop ⇄ Server{RESET}\n"
        f"  {GRAY}{'─' * WIDTH}{RESET}"
    )

    # Dynamic model detection
    nv_key = os.getenv("NVIDIA_API_KEY", "")
    neb_key = os.getenv("NEBIUS_API_KEY", "")

    if nv_key.startswith("nvapi-") or (nv_key and nv_key != "your_nvidia_api_key_here"):
        brain_val = f"{BOLD}NVIDIA Nemotron 70B (build.nvidia.com){RESET}"
    elif neb_key and neb_key != "your_nebius_api_key_here":
        brain_val = f"{BOLD}NVIDIA Nemotron 70B (Nebius Serverless){RESET}"
    else:
        brain_val = f"{GRAY}NVIDIA Nemotron 70B (Offline Fallback Reasoner){RESET}"

    mesh_str = f"Tailscale Encrypted P2P ({tailscale_ip})"

    srv_status = f"{BRIGHT_GREEN}● ONLINE{RESET}" if server_online else f"{GRAY}○ OFFLINE{RESET}"
    lap_status = f"{BRIGHT_GREEN}● ONLINE{RESET}" if laptop_online else f"{GRAY}○ OFFLINE{RESET}"

    node_row1 = "      ┌────────────────────┐          ┌────────────────────┐"
    node_row2 = "      │ 🏠 SERVER NODE     │◄════════►│ 💻 LAPTOP NODE     │"
    node_row3 = f"      │   {srv_status}         │  Tunnel  │   {lap_status}         │"
    node_row4 = "      │   8 services       │          │   Edge daemon      │"
    node_row5 = "      └────────────────────┘          └────────────────────┘"

    status_line = f"   {BRIGHT_GREEN}● SYSTEM OPERATIONAL{RESET}  {DIM}│ Talk via Telegram │ Dual-Node Ready{RESET}"

    lines = [
        "",
        *ascii_art,
        sub_bar,
        "",
        top,
        empty,
        box_row(f"   🧠  {GRAY}Brain Engine{RESET}      {brain_val}"),
        box_row(f"   ⚡  {GRAY}Cognitive Core{RESET}    {YELLOW}Hermes Agent (Multi-Step Tool Calling){RESET}"),
        box_row(f"   🌐  {GRAY}Web Engine{RESET}        {BRIGHT_CYAN}Obscura Stealth Browser (Playwright){RESET}"),
        box_row(f"   💾  {GRAY}Storage Tier{RESET}      {GREEN}Dual Vaults: shared_vault.db + personal_vault.db{RESET}"),
        box_row(f"   🔗  {GRAY}Mesh Tunnel{RESET}       {CYAN}{mesh_str}{RESET}"),
        box_row(f"   📱  {GRAY}Interface{RESET}         {PURPLE}Telegram Natural Language + Voice{RESET}"),
        box_row(f"   🔒  {GRAY}Security{RESET}          {BRIGHT_GREEN}HMAC Auth + User Whitelist + IDOR Protection{RESET}"),
        box_row(f"   💻  {GRAY}Active Node{RESET}       {BOLD}{node_role}{RESET}"),
        empty,
        box_row(node_row1),
        box_row(node_row2),
        box_row(node_row3),
        box_row(node_row4),
        box_row(node_row5),
        empty,
        box_row(status_line),
        empty,
        bot,
        f"  {GRAY}📋 Commands:{RESET}  {BOLD}setup{RESET} │ {BOLD}up{RESET} │ {BOLD}down{RESET} │ {BOLD}test{RESET} │ {BOLD}pair{RESET} │ {BOLD}status{RESET} │ {BOLD}edge{RESET}",
        ""
    ]

    return "\n".join(lines)

def print_banner(
    node_role: str = "Home Server Control Plane",
    tailscale_ip: str = "100.64.0.1",
    server_online: bool = True,
    laptop_online: bool = True
):
    try:
        print(get_banner(node_role, tailscale_ip, server_online, laptop_online))
    except UnicodeEncodeError:
        # Fallback for ultra-restrictive terminals
        print(f"\n✦ NEONCLAW v2.0.0 │ {node_role} │ {tailscale_ip}\n")

if __name__ == "__main__":
    print_banner()

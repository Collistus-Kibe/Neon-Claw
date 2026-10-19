"""
NemoClaw Claude-Code Style Terminal Banner
Provides clean, modern, high-aesthetic startup visuals with live subsystem indicators.
Automatically enables ANSI colors & UTF-8 on Windows cmd.exe and PowerShell.
"""

import os
import sys

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

def get_banner(node_role: str = "Home Server", tailscale_ip: str = "100.64.0.1") -> str:
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

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

    WIDTH = 70  # Inner box content width

    def row(text: str, visual_len: int) -> str:
        pad = max(0, WIDTH - visual_len)
        return f"{BRIGHT_PURPLE}│{RESET}  {text}{' ' * pad}{BRIGHT_PURPLE}│{RESET}"

    border_top = f"{BRIGHT_PURPLE}╭{'─' * (WIDTH + 2)}╮{RESET}"
    border_bottom = f"{BRIGHT_PURPLE}╰{'─' * (WIDTH + 2)}╯{RESET}"
    empty_row = f"{BRIGHT_PURPLE}│{' ' * (WIDTH + 2)}│{RESET}"

    # Header
    title = f"{BOLD}{BRIGHT_CYAN}✦  N E M O C L A W{RESET}  {DIM}v1.0.0{RESET}"
    title_len = 18 + 8  # "✦  N E M O C L A W  v1.0.0" -> 26 visible chars

    sub = f"{DIM}Personal AI Agent • Phone Control • Cloud / Server / Laptop{RESET}"
    sub_len = 59

    # Metadata rows: label (16 chars) + value
    def item(label: str, val_colored: str, val_plain: str) -> str:
        plain_len = 16 + len(val_plain)
        return row(f"{GRAY}{label:<16}{RESET}{val_colored}", plain_len)

    nv_key = os.getenv("NVIDIA_API_KEY", "")
    neb_key = os.getenv("NEBIUS_API_KEY", "")
    
    if nv_key.startswith("nvapi-") or (nv_key and nv_key != "your_nvidia_api_key_here"):
        brain_name = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
        infer_name = "NVIDIA Developer API (build.nvidia.com)"
    elif neb_key and neb_key != "your_nebius_api_key_here":
        brain_name = os.getenv("NEBIUS_MODEL", "nvidia/Llama-3.1-Nemotron-70B-Instruct")
        infer_name = "Nebius Serverless / Token Factory"
    else:
        brain_name = "NVIDIA Nemotron 70B (Dual-Provider)"
        infer_name = "NVIDIA NIM / build.nvidia.com (or Offline Fallback)"

    r_brain = item("Brain Model", f"{BOLD}{brain_name}{RESET}", brain_name)
    r_infer = item("Inference", f"{CYAN}{infer_name}{RESET}", infer_name)
    r_cog = item("Cognitive Core", f"{YELLOW}Hermes Agent (Nous Research Skills Engine){RESET}", "Hermes Agent (Nous Research Skills Engine)")
    r_sand = item("Sandboxing", f"{PURPLE}NVIDIA OpenShell (Landlock + Seccomp BPF){RESET}", "NVIDIA OpenShell (Landlock + Seccomp BPF)")
    r_web = item("Web Engine", f"{BRIGHT_CYAN}Obscura Stealth Headless Browser (Playwright){RESET}", "Obscura Stealth Headless Browser (Playwright)")
    r_tier = item("Storage Tier", f"{GREEN}Dual Vaults: shared_vault.db + personal_vault.db{RESET}", "Dual Vaults: shared_vault.db + personal_vault.db")
    
    mesh_str = f"Tailscale Encrypted Peer-to-Peer ({tailscale_ip})"
    r_mesh = item("Network Mesh", f"{CYAN}{mesh_str}{RESET}", mesh_str)
    
    r_node = item("Active Node", f"{BOLD}{node_role}{RESET}", node_role)

    # Footer status
    status_text = f"{BRIGHT_GREEN}● SYSTEM OPERATIONAL{RESET}  {DIM}│ Talk via Telegram │ Offloading Ready{RESET}"
    status_len = 20 + 2 + 37  # 59 visible chars

    lines = [
        "",
        f"  {border_top}",
        f"  {empty_row}",
        f"  {row(title, title_len)}",
        f"  {row(sub, sub_len)}",
        f"  {empty_row}",
        f"  {r_brain}",
        f"  {r_infer}",
        f"  {r_cog}",
        f"  {r_sand}",
        f"  {r_web}",
        f"  {r_tier}",
        f"  {r_mesh}",
        f"  {r_node}",
        f"  {empty_row}",
        f"  {row(status_text, status_len)}",
        f"  {border_bottom}",
        ""
    ]

    return "\n".join(lines)

def print_banner(node_role: str = "Home Server", tailscale_ip: str = "100.64.0.1"):
    print(get_banner(node_role, tailscale_ip))

if __name__ == "__main__":
    print_banner()

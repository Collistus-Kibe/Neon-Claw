# 🦁 NeonClaw: Unified Dual-Node Personal AI Assistant

> **An open-source personal AI assistant that lives across your laptop and mini home server as one unified mind, commanded from your phone via Telegram. Pull the repo, run setup, and you're live.**

```
  ███╗   ██╗███████╗ ██████╗ ███╗   ██╗ ██████╗██╗      █████╗ ██╗    ██╗
  ████╗  ██║██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔══██╗██║    ██║
  ██╔██╗ ██║█████╗  ██║   ██║██╔██╗ ██║██║     ██║     ███████║██║ █╗ ██║
  ██║╚██╗██║██╔══╝  ██║   ██║██║╚██╗██║██║     ██║     ██╔══██║██║███╗██║
  ██║ ╚████║███████╗╚██████╔╝██║ ╚████║╚██████╗███████╗██║  ██║╚███╔███╔╝
  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ 
  ──────────────────────────────────────────────────────────────────────────
   v2.0.0  │  Open-Source Personal AI  │  Dual-Node: Laptop ⇄ Server
  ──────────────────────────────────────────────────────────────────────────
```

[![NVIDIA Nemotron](https://img.shields.io/badge/Brain-NVIDIA_Nemotron_70B-76B900?logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![Inference](https://img.shields.io/badge/Inference-NVIDIA_API_%2F_Nebius-blue)](https://build.nvidia.com/)
[![Hermes Agent](https://img.shields.io/badge/Engine-Hermes_Agent-purple)](https://nousresearch.com/)
[![Mesh](https://img.shields.io/badge/Mesh-WebSocket_%2B_Tailscale-cyan)](https://tailscale.com/)
[![Security](https://img.shields.io/badge/Security-HMAC_Auth_%2B_Zero_Trust-orange)](https://github.com/nvidia)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 What is NeonClaw?

**NeonClaw** is designed around a single principle: **One Agent, Two Halves**.

Instead of treating your home server and laptop as disconnected computers, NeonClaw acts as a single intelligent assistant that lives on both:
- **🏠 Home Server Node (Always-On):** Runs 24/7 on a mini PC, Raspberry Pi, or home server. Handles Telegram messages from your phone, runs long background tasks, browses the web with stealth Playwright (Obscura), manages memory vaults, and coordinates AI reasoning.
- **💻 Laptop Node (When Available):** Runs locally on your primary workstation. When powered on, it automatically establishes an encrypted tunnel to your server. It gives the agent "hands" on your laptop — running git commands, inspecting local project files, interacting with your clipboard, and opening local links.
- **📱 Phone Control (Telegram):** Talk to your assistant naturally in any chat. No slash commands required. Whitelisted to your personal Telegram User ID.

```
                         📱 Your Phone (Telegram)
                                  │
                    ╔══════════════╧══════════════╗
                    ║     NeonClaw Unified Brain   ║
                    ║   (Feels like ONE assistant) ║
                    ╚══════════════╤══════════════╝
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      │                      ▼
  ┌─────────────────────┐         │        ┌─────────────────────┐
  │ 🏠 SERVER NODE       │         │        │ 💻 LAPTOP NODE       │
  │ (Always-On)          │◄────────┘───────►│ (When Available)     │
  │                      │   Encrypted      │                      │
  │ • Telegram Bot       │   WebSocket      │ • Local File Access  │
  │ • Obscura Browser    │   Tunnel         │ • Git Operations     │
  │ • Redis Task Queue   │ (Tailscale/      │ • IDE Integration    │
  │ • Hermes Agent       │  Direct WS)      │ • Local Code Exec    │
  │ • Shared Vault (DB)  │                  │ • System Clipboard   │
  │ • Personal Vault     │                  │ • Personal Vault     │
  │ • NeonMem API        │                  │ • Heartbeat Reporter │
  └─────────────────────┘                  └─────────────────────┘
```

---

## ⚡ What NeonClaw Can Do (Capabilities)

### 🧠 1. AI & Frontier Reasoning
* **NVIDIA Nemotron 70B Brain:** High-precision reasoning via NVIDIA Developer API (`build.nvidia.com`) or Nebius Serverless.
* **Autonomous Multi-Step Tool Calling:** Hermes Agent executes chains of tools (browse → extract → save memory → reply) without human intervention.
* **Dynamic Intent Routing:** Automatically analyzes requests and routes to specialized execution flows.
* **Zero-Downtime Offline Fallback:** Graceful deterministic responses even if network or API keys are unavailable.
* **Self-Improving Skill Acquisition:** Successful multi-step workflows are synthesized into reusable skills stored in your Shared Vault.

### 🌐 2. Web Automation & Research
* **Obscura Stealth Headless Browser:** Containerized Playwright Chromium with anti-bot evasion techniques.
* **Full-Page Screenshots to Phone:** Captures live webpages and streams photos directly into your Telegram chat.
* **Clean Text Extraction:** Extracts core article and documentation text from any URL.
* **HTTP Fallback Scraper:** Fast, lightweight raw scraping fallback if browser rendering is unnecessary.

### 💾 3. Dual-Tier Memory & Persistence
* **Shared Vault (`shared_vault.db`):** Long-term facts, user preferences, and synthesized skills synced across nodes.
* **Personal Vault (`personal_vault.db`):** Node-private secrets, hardware telemetry, and local paths that never leave that device.
* **IDOR-Protected Operations:** Row-level ownership validation ensures only authorized users can read or delete memories.
* **Skills Registry:** Browse, recall, and manage learned automated workflows over time.

### 📱 4. Mobile Interface & Control
* **Natural Language Telegram Bot:** Chat casually without mandatory `/ask` prefixes.
* **Voice Note Support:** Send Telegram audio notes directly for transcription and processing.
* **User ID Whitelisting:** Strictly locked to authorized Telegram user IDs (`ALLOWED_TELEGRAM_USER_IDS`).
* **Live System Status:** Check CPU, RAM, battery, active models, and node connectivity directly from your phone.

### 🔒 5. Security & Isolation
* **Zero Trust Between Nodes:** Inter-node WebSocket communication is authenticated via HMAC signing and pairing secrets.
* **Localhost-Only Bindings:** All internal service ports are bound strictly to `127.0.0.1`.
* **Subprocess Command Allowlist:** Laptop execution engine enforces strict allowlists to prevent arbitrary code injection.
* **NVIDIA OpenShell Compatibility:** Designed for kernel-level sandboxing (Landlock + Seccomp BPF).

### 🖥️ 6. Dual-Node Distributed Mesh
* **NeonBridge Tunnel:** Persistent WebSocket connection over Tailscale P2P (100.64.x.x) or direct HTTPS fallback.
* **One-Time Pairing Code:** Seamlessly pair server and laptop with a 6-character handshake (`nemoclaw pair`).
* **Intelligent Task Offloading:** The agent decides where tasks belong — heavy browsing on server, git and files on laptop.
* **Auto-Reconnect & Telemetry:** Laptop continuously syncs telemetry (CPU, RAM, battery, status) with exponential backoff reconnects.

---

## 🚀 Setup Flow (Clone → Configure → Run)

### 1. Clone & Enter Directory
```bash
git clone https://github.com/youruser/neon-claw.git
cd neon-claw
```

### 2. Configure via Interactive Wizard (< 60s)
```bash
python nemoclaw.py setup
```
*(On Windows you can just run `nemoclaw setup`)*

The wizard will guide you through:
1. **Node Role:** Select `server` (for mini PC / home server) or `laptop`
2. **Telegram Bot Token:** From [@BotFather](https://t.me/botfather) *(server only)*
3. **Telegram User ID:** From [@userinfobot](https://t.me/userinfobot) to whitelist your phone
4. **NVIDIA API Key:** From [build.nvidia.com](https://build.nvidia.com/) (format: `nvapi-...`) or Nebius Studio
5. **Tailscale Mesh Detection:** Auto-detects 100.x.x.x peer IP

### 3. Start the Nodes

#### On your Home Server:
```bash
nemoclaw up
```
*Brings up the 24/7 server mesh with Docker Compose (or `--native` for pure Python mode).*

#### On your Workstation Laptop:
```bash
nemoclaw pair
```
*Enter the one-time 6-character code from your server to establish the secure tunnel, then run:*
```bash
nemoclaw edge
```

---

## 📋 CLI Reference

| Command | Description |
| :--- | :--- |
| `nemoclaw` / `nemoclaw status` | Show Claude-Code style banner, live dual-node indicators, & credentials state |
| `nemoclaw setup` | Interactive terminal wizard to configure tokens and roles |
| `nemoclaw up` | Start Home Server mesh containers |
| `nemoclaw pair` | Pair laptop and server nodes into unified mesh |
| `nemoclaw edge` | Launch laptop edge worker daemon |
| `nemoclaw test` | Run end-to-end verification test suite |
| `nemoclaw down` | Stop all containers |

---

## 🏗️ Architecture & Engineering

For deep architectural details, protocol specifications, and security audits, read **[engineering.md](file:///c:/Users/Admin/OneDrive/Documentos/Neon%20Claw/engineering.md)**.

---

## 📄 License

MIT License. Designed for personal sovereignty, distributed intelligence, and autonomous pair programming.

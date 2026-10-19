# 🦁 NemoClaw: Always-On Private Personal AI Assistant

> **Always-on private personal AI agent commanded from your phone via Telegram. Operates seamlessly across your Home Server, Cloud, and Laptop with distributed task offloading, self-learning skills, and private Dual-Tier Vaults.**

[![NVIDIA Nemotron](https://img.shields.io/badge/Brain-NVIDIA_Nemotron_70B-76B900?logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![Inference](https://img.shields.io/badge/Inference-NVIDIA_API_%2F_Nebius-blue)](https://build.nvidia.com/)
[![Hermes Agent](https://img.shields.io/badge/Engine-Hermes_Agent-purple)](https://nousresearch.com/)
[![Security](https://img.shields.io/badge/Sandbox-NVIDIA_OpenShell-orange)](https://github.com/nvidia)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Overview

**NemoClaw** bridges state-of-the-art open-weights reasoning with total data sovereignty. Commanded directly from your phone via Telegram, it operates seamlessly across your **Home Server**, **Cloud Host**, and **Workstation Laptop**. 

Deploy it 24/7 on your home server or a cloud virtual machine to handle web research, background monitoring, and message intake, while offloading workstation-specific tasks (local code, local files, and git) to your laptop via Tailscale.

```
                             📱 Mobile Phone (Telegram Bot)
                                        │
                                        ▼ (Natural Chat & Voice, Whitelisted)
       ┌────────────────────────────────────────────────────────┐
       │             🏠 Always-On Home Server Node              │
       │                                                        │
       │  ┌──────────────────────────────────────────────────┐  │
       │  │             🛡️ NVIDIA OpenShell Sandbox           │  │
       │  │                                                  │  │
       │  │  🧠 Hermes Agent Loop   🌐 Obscura Stealth       │  │
       │  │     (Skills & Memory)      (Headless Browser)    │  │
       │  │          │                      │                │  │
       │  └──────────┼──────────────────────┼────────────────┘  │
       │             │                      │                   │
       │             ▼                      ▼ Live Screenshot   │
       │  ⚡ NVIDIA Developer API / NIM  Telegram Media Delivery│
       │     (nvidia/llama-3.1-nemotron-70b-instruct)           │
       │                                                        │
       │  💾 Dual-Tier Storage Layer:                           │
       │     ├── 🌐 Shared Vault DB (Memories & Skills)         │
       │     └── 🔒 Server Personal DB (Private Node Secrets)   │
       └────────────────────────────┬───────────────────────────┘
                                    │
                🔐 Encrypted Peer-to-Peer Tunnel (Tailscale)
                                    │
       ┌────────────────────────────▼───────────────────────────┐
       │              💻 Workstation Laptop Node                │
       │                                                        │
       │  ⚡ nemoclaw-edge daemon (Heartbeat & Task Runner)      │
       │  💾 Laptop Personal DB (Local files & IDE credentials) │
       │  🔄 Bi-directional Offload (Heavy Tasks -> Server)     │
       └────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

* **🧠 Frontier Reasoning via NVIDIA Nemotron**: Powered by `nvidia/llama-3.1-nemotron-70b-instruct` served via **NVIDIA Developer API (`build.nvidia.com`)** or **Nebius Serverless**, with deterministic zero-downtime offline fallback.
* **🛠️ Hermes Agent & Reusable Skills**: Autonomous multi-step function calling loop that synthesizes successful workflows into reusable skills stored in your Shared Vault.
* **🌐 Obscura Stealth Headless Browser**: Containerized Playwright Chromium engine with evasive stealth headers. Navigates pages, bypasses anti-bot walls, and sends full-page screenshots directly to your phone via Telegram.
* **💾 Dual-Tier Storage Architecture**:
  * **Shared Vault (`shared_vault.db`)**: Synchronized long-term memories and acquired skills.
  * **Personal Vault (`personal_vault.db`)**: Local node secrets, hardware telemetry, and local filesystem paths that never leave the host machine.
* **📱 Natural Telegram Interface**: Text or send voice notes directly to your assistant without `/ask` prefixes. Includes user whitelist security (`ALLOWED_TELEGRAM_USER_IDS`).
* **🛡️ NVIDIA OpenShell Sandboxing**: Kernel-level isolation using Linux Landlock and Seccomp BPF syscall filtering to guarantee safe agent execution.
* **💻 Laptop $\leftrightarrow$ Server Offloading Mesh**: Connect your laptop over Tailscale to offload long-running background tasks to your 24/7 server or execute workstation-local actions.

---

## ⚡ Quickstart
 
### 1. Fast Setup (Interactive CLI Wizard)
Run the built-in configuration wizard:
```bash
python nemoclaw.py setup
```
*or simply:*
```cmd
nemoclaw setup
```
Follow the interactive prompts to enter:
1. **Telegram Bot Token** (from [@BotFather](https://t.me/botfather))
2. **Telegram User ID** (from [@userinfobot](https://t.me/userinfobot) to whitelist your phone)
3. **NVIDIA Developer API Key** (from [build.nvidia.com](https://build.nvidia.com/) — format: `nvapi-...` with free developer credits, or Nebius key)

### 2. Launch Home Server Mesh
```cmd
nemoclaw up
```
Brings up all 8 microservices via Docker Compose (`redis`, `neoncore`, `neonmesh`, `obscura`, `neonmem`, `neonshell`, `neonvault`, `neonpulse`).

### 3. Verify Health
```cmd
nemoclaw test
```

### 4. Connect Laptop Node (Optional)
On your laptop:
```bash
python nemoclaw.py edge
```

---

## 📋 CLI Reference

| Command | Description |
| :--- | :--- |
| `nemoclaw` | Display Claude-Code style status banner & credentials health |
| `nemoclaw setup` | Interactive terminal wizard to configure tokens |
| `nemoclaw up` | Start Home Server Docker Compose mesh |
| `nemoclaw down` | Stop all containers |
| `nemoclaw test` | Run end-to-end verification test suite |
| `nemoclaw edge` | Launch laptop edge worker daemon |

---

## 📄 License
MIT License. Built for data sovereignty and autonomous personal AI.

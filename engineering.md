# ENGINEERING.MD - CORE PROJECT STATE

> **CRITICAL RULE FOR AI AGENTS:** You must read this file before suggesting any architectural changes. ANY time you write, modify, or delete code in this project during our session, you MUST output the required updates to this `engineering.md` file to reflect the new state. Do not skip this step.

> **Last Updated:** 2026-10-25T20:08:00+03:00  
> **System Version:** NeonClaw v2.0 (Unified Dual-Node Personal AI Agent)

---

## 1. Project Overview & Architecture v2

**NeonClaw** is an always-on, privacy-first personal AI assistant that operates across a **Home Server**, **Workstation Laptop**, and **Mobile Phone (via Telegram)** as **one unified entity**. 

Instead of feeling like two separate systems, NeonClaw acts as a single mind with two physical nodes:
1. **🏠 Server Node (Always-On):** Runs Telegram bot, task queue, autonomous multi-step Hermes agent, Obscura stealth browser, memory API, and shared/personal vaults.
2. **💻 Laptop Node (When Available):** Runs lightweight edge daemon with local tools (shell command execution, git repo management, local filesystem access, clipboard, system browser).
3. **📱 Mobile Control (Telegram):** Natural language interface from your phone with user ID whitelisting, media delivery, and remote status checks.
4. **🔗 NeonBridge (Mesh Tunnel):** Persistent, encrypted WebSocket tunnel connecting Laptop ⇄ Server over Tailscale/WireGuard or direct WS fallback with HMAC message authentication.

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
  │ • Hermes Agent       │  WireGuard/      │ • Local Code Exec    │
  │ • Shared Vault (DB)  │  Direct WS)      │ • System Clipboard   │
  │ • Personal Vault     │                  │ • Personal Vault     │
  │ • NeonMem API        │                  │ • Heartbeat Reporter │
  └─────────────────────┘                  └─────────────────────┘
```

### Technology Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Brain Model  | NVIDIA Nemotron 70B via NVIDIA Developer API (`build.nvidia.com`) or Nebius Serverless (`api.studio.nebius.ai/v1`) |
| Cognitive    | Hermes Agent (Nous Research) with multi-step tool execution & autonomous skill acquisition |
| Sandboxing   | NVIDIA OpenShell architectural model (Landlock, Seccomp BPF, allowlisted command execution) |
| Web Browser  | Obscura Headless Browser (Playwright Stealth + Chromium Sandbox + HTTP fallback) |
| Inter-Node Tunnel | NeonBridge: Persistent WebSocket tunnel over Tailscale P2P (100.64.x.x) or direct HTTPS fallback |
| Storage      | Dual Vaults: `shared_vault.db` (synced memories & skills) + `personal_vault.db` (local node secrets & telemetry) |
| Mobile Bot   | Telegraf (Telegram Bot API, voice & direct text, media streaming) |
| Runtime      | Python 3.11, Node.js 20 (Alpine for Docker mode) |
| CLI Plane    | `nemoclaw.py` unified CLI (`setup`, `up`, `down`, `test`, `pair`, `edge`, `status`) |

---

## 2. Current State & Subsystems

### What Works
- ✅ **Upgraded Terminal Banner v2** — High-aesthetic ASCII art, ANSI gradient colors, and live dual-node indicators (`neon-claw/banner.py`)
- ✅ **Unified CLI Control Plane** (`nemoclaw.py`, `nemoclaw.bat`, `nemoclaw.ps1`) — Setup wizard, credentials verification, status view, pairing stub, and execution control
- ✅ **Dual-Provider Frontier LLM Client** (`nebius_client.py`) — Supports NVIDIA Developer API (`build.nvidia.com`), Nebius Serverless, and zero-downtime offline fallback
- ✅ **Autonomous Hermes Agent** (`hermes_agent.py`) — Multi-step tool loop (browsing, memory recall/storage, skill synthesis)
- ✅ **Dual-Tier Database Architecture** (`vault.py`, `shared_schema.sql`, `personal_schema.sql`) — Isolated shared vault and personal vault
- ✅ **Obscura Stealth Browser** (`obscura/server.py`) — Playwright Chromium with bot-detection evasions and full-page screenshot capture
- ✅ **Natural Language Telegram Bot** (`neonpulse/bot.js`) — Direct conversational text, user whitelist security, media photo delivery
- ✅ **Task Queue Pipeline** (`neoncore/taskQueue.js`) — Redis BullMQ orchestrating route → agent → memory → reply
- ✅ **Laptop Edge Daemon** (`nemoclaw-edge/edge_daemon.py`) — Telemetry collection (CPU, RAM, disk, battery, Tailscale IP)
- ✅ **Repository Hygiene & Dead Code Cleanup** — 11 empty/unused directories and all `__pycache__` artifacts permanently removed

### Active Roadmap (v2 Dual-Node Evolution)

#### Phase 1: Cleanup & Foundation (COMPLETED ✅)
- [x] Full codebase audit and scan
- [x] Remove dead directories (`src/`, `config/`, `data/`, `neonmesh/brain_interface/`, `neonmem/backends/`, `__pycache__/`)
- [x] Banner upgrade to v2 with ASCII art and dual-node indicators
- [x] Update `engineering.md` and `README.md`

#### Phase 2: NeonBridge WebSocket Mesh Tunnel (NEXT)
- [ ] Create `neon-claw/neonbridge/` (WebSocket server + client)
- [ ] Implement NeonClaw Mesh Protocol (NMP) with HMAC message signing
- [ ] Pairing handshake (`nemoclaw pair` with 6-char one-time exchange)
- [ ] Auto-reconnect with exponential backoff & latency tracking

#### Phase 3: Laptop Task Execution Engine
- [ ] Upgrade `edge_daemon.py` with local execution capabilities:
  - `exec_command` with strict allowlist
  - `read_file` / `write_file` for local project access
  - `git_status` / `git_diff` / `git_commit`
  - `clipboard_read` / `clipboard_write`
  - `open_url` in default host desktop browser

#### Phase 4: Intelligent Dual-Node Routing
- [ ] Hermes Agent routing heuristics: server vs. laptop execution target
- [ ] Capability advertisement and offline task queuing

#### Phase 5: Pure Python Native Stack (Zero Docker Option)
- [ ] Python Telegram Bot (`aiogram` / `python-telegram-bot`)
- [ ] In-process task queue (`asyncio.Queue` + SQLite)
- [ ] Single-command native runner (`nemoclaw up --native`)

#### Phase 6: Voice Notes & Semantic Memory
- [ ] Whisper voice transcription for `.ogg` Telegram voice notes
- [ ] Sentence-transformers embedding search in `neonmem`

---

## 3. File Structure v2

```
Neon Claw/                                  # Project root (GitHub repo)
├── README.md                               # Showcase & quickstart documentation
├── LICENSE                                 # MIT License
├── .gitignore                              # Protects .env, .db, and cache files
├── engineering.md                          # THIS FILE — project state & architecture
├── nemoclaw.py                             # 🎯 Unified CLI: setup, up, down, test, pair, edge
├── nemoclaw.bat                            # Windows cmd.exe launcher
├── nemoclaw.ps1                            # Windows PowerShell launcher
│
└── neon-claw/                              # Services directory
    ├── banner.py                           # ⬆️ UPGRADED v2: ASCII art + dual-node banner
    ├── compat.py                           # Starlette/FastAPI compatibility shim
    ├── docker-compose.yml                  # Docker orchestration (server mode)
    ├── .env.example                        # Environment template
    ├── test_system.py                      # Verification test suite
    │
    ├── neoncore/                           # Task Dispatcher (Node.js for Docker)
    │   ├── Dockerfile
    │   ├── package.json
    │   ├── index.js
    │   ├── router.js
    │   ├── taskQueue.js
    │   └── banner.js
    │
    ├── neonmesh/                           # Agent Engine (Python)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── main.py
    │   ├── nebius_client.py                # Dual NVIDIA/Nebius client + offline fallback
    │   └── agents/
    │       ├── __init__.py
    │       ├── base_agent.py
    │       ├── hermes_agent.py             # Multi-step tool loop & skill synthesizer
    │       └── router_agent.py
    │
    ├── neonmem/                            # Memory API (Python)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── api.py                          # Remember, recall, forget, skills, reflect
    │
    ├── neonvault/                          # Dual Vault Persistence (Python)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── shared_schema.sql               # Memories, skills
    │   ├── personal_schema.sql             # Node secrets, telemetry
    │   └── vault.py
    │
    ├── neonpulse/                          # Telegram Bot (Node.js for Docker)
    │   ├── Dockerfile
    │   ├── package.json
    │   ├── bot.js                          # Natural language Telegram interface
    │   ├── banner.js
    │   └── formatter.js
    │
    ├── neonshell/                          # Network Monitor (Python)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── shell.py                        # Network mode & Tailscale awareness
    │
    ├── obscura/                            # Stealth Browser (Playwright / Chromium)
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── server.py                       # Stealth navigation & screenshot capture
    │
    ├── neonbridge/                         # 🆕 WebSocket Mesh Tunnel (In Progress)
    │   ├── __init__.py
    │   ├── server.py                       # WS server (runs on server node)
    │   ├── client.py                       # WS client (runs on laptop node)
    │   ├── protocol.py                     # NMP message protocol + HMAC signing
    │   └── pairing.py                      # One-time pairing code handshake
    │
    └── nemoclaw-edge/                      # Laptop Node Worker (Python)
        ├── edge_daemon.py                  # Telemetry & task executor
        ├── local_tools.py                  # 🆕 Filesystem, git, clipboard, shell tools
        └── requirements.txt
```

---

## 4. Change Log

| Date       | Change                                      | Files Affected                 |
|------------|---------------------------------------------|-------------------------------|
| 2026-06-04 | Initial `engineering.md` created from full scan | `engineering.md` (NEW)        |
| 2026-10-18 | Architecture & Implementation Plan: Personal Agent (Home Server + Laptop Offloading + Obscura Headless Browser + Telegram Phone UX) | `engineering.md`, `neon_claw_implementation_plan.md` |
| 2026-10-18 | Architecture Evolution: NemoClaw Stack (NVIDIA Nemotron via Nebius Serverless, Hermes Agent, OpenShell Sandboxing, Dual Shared/Personal Vaults) | `engineering.md`, `neon_claw_personal_ai_system_plan.md` |
| 2026-10-18 | Implemented NemoClaw Core: Dual-Tier Vaults (shared + personal), Hermes Agent loop, Nebius Nemotron client, Obscura stealth browser, Telegram whitelist & natural chat, Laptop edge daemon | `neonvault/*`, `neonmem/api.py`, `neonmesh/*`, `obscura/*`, `neoncore/taskQueue.js`, `neonpulse/bot.js`, `nemoclaw-edge/*`, `docker-compose.yml`, `test_system.py` |
| 2026-10-18 | Added Claude-Code Style Startup Banner & Unified CLI Control Plane (`nemoclaw.py`, `nemoclaw.bat`, `nemoclaw.ps1`, `banner.py`, `banner.js`) | `nemoclaw.py`, `nemoclaw.bat`, `nemoclaw.ps1`, `neon-claw/banner.py`, `neon-claw/banner.js`, `neoncore/index.js`, `neonpulse/bot.js` |
| 2026-10-18 | Prepared for GitHub: Created root `README.md` showcase and `.gitignore` to protect `.env` secrets & SQLite databases | `README.md`, `.gitignore` |
| 2026-10-18 | Added NVIDIA Developer API (build.nvidia.com) support: Auto-detects `nvapi-...` keys, integrates `integrate.api.nvidia.com/v1`, updated setup wizard & compose | `nebius_client.py`, `nemoclaw.py`, `docker-compose.yml`, `.env.example`, `engineering.md` |
| 2026-10-22 | **NeonClaw v2.0 Architecture Approved & Phase 1 Execution**: Cleaned dead scaffolding directories (`src/`, `config/`, `data/`, `neonmesh/brain_interface/`, `neonmem/backends/`, `__pycache__/`), upgraded terminal banner with large ASCII art and dual-node visual status indicators, added `nemoclaw pair` CLI capability, updated `engineering.md` and `README.md` | `nemoclaw.py`, `neon-claw/banner.py`, `engineering.md`, `README.md` |
| 2026-10-25 | Fixed missing `eventBus` import in `neoncore/index.js` and repaired test runner entrypoint/indentation in `test_system.py`; 100% test pass verified across dual vaults, IDOR guards, and Hermes Agent | `neoncore/index.js`, `test_system.py`, `engineering.md` |

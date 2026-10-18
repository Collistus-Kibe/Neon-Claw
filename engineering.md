# ENGINEERING.MD - CORE PROJECT STATE

> **CRITICAL RULE FOR AI AGENTS:** You must read this file before suggesting any architectural changes. ANY time you write, modify, or delete code in this project during our session, you MUST output the required updates to this `engineering.md` file to reflect the new state. Do not skip this step.

> **Last Updated:** 2026-10-18T20:41:00+03:00

---

## 1. Project Overview & Architecture

**NemoClaw (Neon Claw)** is an always-on, privacy-first personal AI assistant operating across an **Always-On Home Server**, **Workstation Laptop**, and **Mobile Phone (via Telegram)**. It combines frontier reasoning from open-source NVIDIA models (`nvidia/Llama-3.1-Nemotron-70B-Instruct`) with strict kernel-level sandboxing (NVIDIA OpenShell), self-improving skill acquisition (Hermes Agent), an open-source headless browser (Obscura), and a **Dual-Tier Database Architecture** (Shared + Personal Vaults).

### Technology Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Brain Model  | `nvidia/Llama-3.1-Nemotron-70B-Instruct` via Nebius Serverless (`api.studio.nebius.ai/v1`) |
| Cognitive    | Hermes Agent (Nous Research) with autonomous skill acquisition |
| Sandboxing   | NVIDIA OpenShell (Linux Landlock, Seccomp BPF, OPA network policies) |
| Web Browser  | Obscura Headless Browser (Playwright Stealth + Chromium Sandbox) |
| Runtime      | Node.js 20 (Alpine), Python 3.11   |
| Orchestrator | Docker Compose (NemoClaw Core)     |
| Queue        | Redis 7 (Alpine) + BullMQ 4.14     |
| HTTP Server  | Express 4.18 (JS), FastAPI (Python) |
| HTTP Client  | Axios 1.6 (JS), httpx (Python)     |
| Databases    | Dual Vaults: `shared_vault.db` (sync) + `personal_vault.db` (per-node) |
| Mobile Bot   | Telegraf 4.15 (Telegram Bot API, voice & direct text) |
| Mesh Tunnel  | WireGuard / Tailscale (Home Server <-> Laptop Offloading) |

### Inter-Service Communication Map

| Source    | Target   | Protocol   | Endpoint(s)                            |
|-----------|----------|------------|----------------------------------------|
| NeonPulse | Redis    | BullMQ     | Queue: `neon-tasks`                    |
| NeonCore  | Redis    | BullMQ     | Queue: `neon-tasks` (worker), `neon-replies` (producer) |
| NeonPulse | Redis    | BullMQ     | Queue: `neon-replies` (worker)         |
| NeonCore  | NeonMesh | HTTP POST  | `/router`, `/agent/{agent_type}`       |
| NeonCore  | NeonMem  | HTTP POST  | `/remember`                            |
| NeonMem   | NeonVault| HTTP POST/GET/DELETE | `/memories`, `/memories/{id}` |
| NeonPulse | NeonMem  | HTTP POST  | `/recall` (via `/memory` command)      |

---

## 2. Current State & Recent Changes

### Working State: **Skeleton / Stubs Only**

The entire system boots and wires together, but **all AI "brain" logic is stubbed**. Every agent returns hardcoded placeholder strings. The system is architecturally complete for the happy path but has zero real intelligence.

### What Works
- ✅ Docker Compose brings up all 7 containers (redis, neoncore, neonmesh, neonmem, neonpulse, neonshell, neonvault)
- ✅ Telegram bot connects (if `TELEGRAM_BOT_TOKEN` is set) and accepts `/start`, `/ask`, `/mode`, `/memory`, `/status` commands
- ✅ Task queue pipeline: NeonPulse → Redis → NeonCore → NeonMesh → NeonMem → NeonVault (full round-trip)
- ✅ Reply pipeline: NeonCore enqueues to `neon-replies`, NeonPulse worker delivers to Telegram
- ✅ NeonVault SQLite persistence (schema auto-created on startup)
- ✅ NeonShell mode detection (live/dark) written to shared volume

### What Is Stubbed / Not Implemented
- ❌ **Brain Interface** — `brain_interface/stub.py` returns hardcoded strings; no LLM connected
- ❌ **Router Logic** — Always returns `"research"` regardless of prompt
- ❌ **Memory Backends** — `chroma_backend.py`, `redis_backend.py`, `sqlite_backend.py` are all empty placeholders
- ❌ **Memory Consolidation** — `consolidation.py` is a placeholder (intended for decay/REM cycles)
- ❌ **NeonMem Reflect** — `/reflect` endpoint logs but does nothing meaningful
- ❌ **Natural Language Mode** — Bot requires slash commands (`/ask`); no free-text handling
- ❌ **src/agents/** — Empty directory (unused)
- ❌ **src/mcp/** — Empty directory (unused)
- ❌ **config/bob_settings.json** — Empty file

### Known Issues & Risks
- `@app.on_event("startup")` in NeonVault is deprecated in newer FastAPI; should migrate to lifespan handler
- NeonPulse `bot.command('status')` is hardcoded — does not actually ping services
- No health checks configured in `docker-compose.yml`
- No `.env` file shipped (only `.env.example`); deployment requires manual setup
- `neon_mode.txt` shared volume path assumes Linux containers; NeonShell pings `8.8.8.8` which may fail in restricted networks

### Recent Session Context (from conversation history)
1. **DeepSeek API Integration** — Work began on connecting `OLLAMA_CLOUD_API_KEY_1` via a test script to replace brain stubs
2. **Natural Language Bot Refactor** — Intent to remove mandatory `/ask` slash commands and handle all text as AI prompts
3. **Database Init Fixes** — SQLite initialization errors were investigated and resolved in prior sessions

---

## 3. Active Tasks / Roadmap (Personal Agent Architecture)

### Phase 1: Security Hardening & Zero-Trust Base
- [x] **Close Exposed Ports** — Restricted host port mappings to `127.0.0.1` for `redis`, `neonmesh`, `neonmem`, `neonvault`
- [x] **Telegram User Whitelisting** — Enforced `ALLOWED_TELEGRAM_USER_IDS` in `neonpulse/bot.js`
- [x] **Fix IDOR in NeonVault** — Scoped `user_id` validation for memory deletion in `vault.py`
- [x] **Add Request Timeouts** — Configured explicit timeouts on Axios and HTTPX requests

### Phase 2: Natural Telegram UX & LLM Brain Activation
- [x] **Connect Real LLM Brain** — Implemented `nebius_client.py` with `nvidia/Llama-3.1-Nemotron-70B-Instruct` and offline fallback
- [x] **Hermes Agent Cognitive Engine** — Built `agents/hermes_agent.py` with tool execution and self-improving skills
- [x] **Natural Language Bot** — Implemented `bot.on('text')` in `neonpulse/bot.js` (no `/ask` needed)
- [x] **Intelligent Intent Router** — Dynamic classification in `router_agent.py`

### Phase 3: Obscura Headless Browser Worker
- [x] **Playwright Stealth Container** — Built `neon-claw/obscura/` service with Playwright Chromium & stealth evasions
- [x] **Web Automation Tools** — Implemented `/navigate` and full-page screenshot capture
- [x] **Telegram Media Streaming** — Forwarding base64 screenshots to Telegram chat via `replyWorker`

### Phase 4: Dual Vault & Laptop Hybrid Offloading Mesh
- [x] **Dual-Tier Database Architecture** — Separated `shared_vault.db` (memories, skills) and `personal_vault.db` (local secrets, telemetry)
- [x] **Tailscale Network Awareness** — Added Tailscale peer detection in `neonshell/shell.py`
- [x] **Laptop Edge Daemon** — Built `nemoclaw-edge/edge_daemon.py` for workstation telemetry and offload execution

### Phase 5: Voice Notes & Semantic Vector Memory (Next Steps)
- [ ] **Telegram Voice Note Transcription** — Transcribe `.ogg` voice notes via Whisper
- [ ] **Vector Memory Integration** — Vector embeddings and semantic recall in `neonmem`

---

## 4. File Structure & Component Roles

```
Neon Claw/                              # Project root
├── engineering.md                      # THIS FILE — project state (source of truth)
├── config/
│   └── bob_settings.json               # Bot persona/settings config (EMPTY)
├── data/                               # Runtime data directory (EMPTY)
├── src/
│   ├── agents/                         # Future agent code (EMPTY)
│   └── mcp/                            # Future MCP integration (EMPTY)
└── neon-claw/                          # Microservices root
    ├── README.md                       # Setup instructions
    ├── .env.example                    # Template: TELEGRAM_BOT_TOKEN
    ├── docker-compose.yml              # Orchestrates all 7 containers
    │
    ├── neoncore/                       # ORCHESTRATOR — Central task dispatcher
    │   ├── Dockerfile                  #   Node.js 20 Alpine, port 3000
    │   ├── package.json                #   express, bullmq, ioredis, axios
    │   ├── index.js                    #   Express server, POST /ask → enqueues to BullMQ
    │   ├── router.js                   #   Calls NeonMesh /router to classify prompt intent
    │   ├── taskQueue.js                #   BullMQ worker: route → call agent → save memory → reply
    │   └── eventBus.js                 #   Node EventEmitter (unused, scaffolding)
    │
    ├── neonmesh/                       # AGENT MESH — AI agent dispatch + brain interface
    │   ├── Dockerfile                  #   Python 3.11, uvicorn, port 8001
    │   ├── requirements.txt            #   fastapi, uvicorn, httpx, python-dotenv
    │   ├── main.py                     #   FastAPI: POST /router, POST /agent/{type}
    │   ├── brain_interface/
    │   │   ├── __init__.py
    │   │   └── stub.py                 #   Stub functions: generate_router, generate_primary,
    │   │                               #     generate_deep, transcribe_audio, analyze_image
    │   └── agents/
    │       ├── __init__.py
    │       ├── base_agent.py           #   BaseAgent ABC with process() method
    │       ├── router_agent.py         #   Routes via brain stub (always returns "research")
    │       ├── research_agent.py       #   Calls generate_primary(prompt, "Research context")
    │       ├── code_agent.py           #   Calls generate_primary(prompt, "Code context")
    │       ├── write_agent.py          #   Calls generate_primary(prompt, "Write context")
    │       └── analyze_agent.py        #   Calls analyze_image(b'', prompt)
    │
    ├── neonmem/                        # MEMORY LAYER — Abstraction over storage backends
    │   ├── Dockerfile                  #   Python 3.11, uvicorn, port 8002
    │   ├── requirements.txt            #   fastapi, uvicorn, httpx
    │   ├── api.py                      #   FastAPI: /remember, /recall, /forget/{id}, /reflect
    │   ├── consolidation.py            #   Placeholder for decay/REM cycles
    │   └── backends/
    │       ├── __init__.py
    │       ├── chroma_backend.py       #   Placeholder (EMPTY)
    │       ├── redis_backend.py        #   Placeholder (EMPTY)
    │       └── sqlite_backend.py       #   Placeholder (EMPTY)
    │
    ├── neonpulse/                      # USER INTERFACE — Telegram bot
    │   ├── Dockerfile                  #   Node.js 20 Alpine
    │   ├── package.json                #   telegraf, bullmq, ioredis, axios, dotenv
    │   ├── bot.js                      #   Telegraf bot: /start, /ask, /mode, /memory, /status
    │   │                               #     + BullMQ worker for neon-replies → Telegram delivery
    │   └── formatter.js                #   Wraps responses with "[Agent Response]\n" prefix
    │
    ├── neonshell/                      # ENVIRONMENT MONITOR — Network mode detection
    │   ├── Dockerfile                  #   Python 3.11
    │   ├── requirements.txt            #   schedule, python-dotenv
    │   └── shell.py                    #   Pings 8.8.8.8 every 30s → writes "live"/"dark" to
    │                                   #     /shared/neon_mode.txt (shared Docker volume)
    │
    └── neonvault/                      # PERSISTENCE — SQLite database backend
        ├── Dockerfile                  #   Python 3.11, uvicorn, port 8003
        ├── requirements.txt            #   fastapi, uvicorn, aiosqlite
        ├── schema.sql                  #   Table: memories (id, content, user_id, agent_id, tags, created_at)
        └── vault.py                    #   FastAPI: POST /memories, GET /memories, DELETE /memories/{id}
                                        #     Auto-creates /data/neonvault.db on startup
```

### Service Port Map

| Service    | Internal Port | External Port | Language   |
|------------|--------------|---------------|------------|
| Redis      | 6379         | 6379          | —          |
| NeonCore   | 3000         | (internal)    | Node.js    |
| NeonMesh   | 8001         | 8001          | Python     |
| NeonMem    | 8002         | 8002          | Python     |
| NeonVault  | 8003         | 8003          | Python     |
| NeonPulse  | —            | —             | Node.js    |
| NeonShell  | —            | —             | Python     |

### Environment Variables

| Variable               | Used By               | Purpose                              |
|------------------------|-----------------------|--------------------------------------|
| `TELEGRAM_BOT_TOKEN`   | NeonPulse             | Telegram Bot API authentication      |
| `REDIS_HOST`           | NeonCore, NeonPulse   | Redis connection host (default: `redis`) |
| `REDIS_PORT`           | NeonCore, NeonPulse   | Redis connection port (default: `6379`)  |
| `NEONMESH_URL`         | NeonCore              | NeonMesh base URL (default: `http://neonmesh:8001`) |
| `NEONMEM_URL`          | NeonCore, NeonPulse   | NeonMem base URL (default: `http://neonmem:8002`)   |
| `NEONVAULT_URL`        | NeonMem               | NeonVault base URL (default: `http://neonvault:8003`) |

---

## 5. Change Log

| Date       | Change                                      | Files Affected                 |
|------------|---------------------------------------------|-------------------------------|
| 2026-06-04 | Initial `engineering.md` created from full scan | `engineering.md` (NEW)        |
| 2026-10-18 | Architecture & Implementation Plan: Personal Agent (Home Server + Laptop Offloading + Obscura Headless Browser + Telegram Phone UX) | `engineering.md`, `neon_claw_implementation_plan.md` |
| 2026-10-18 | Architecture Evolution: NemoClaw Stack (NVIDIA Nemotron via Nebius Serverless, Hermes Agent, OpenShell Sandboxing, Dual Shared/Personal Vaults) | `engineering.md`, `neon_claw_personal_ai_system_plan.md` |
| 2026-10-18 | Implemented NemoClaw Core: Dual-Tier Vaults (shared + personal), Hermes Agent loop, Nebius Nemotron client, Obscura stealth browser, Telegram whitelist & natural chat, Laptop edge daemon | `neonvault/*`, `neonmem/api.py`, `neonmesh/*`, `obscura/*`, `neoncore/taskQueue.js`, `neonpulse/bot.js`, `nemoclaw-edge/*`, `docker-compose.yml`, `test_system.py` |
| 2026-10-18 | Added Claude-Code Style Startup Banner & Unified CLI Control Plane (`nemoclaw.py`, `nemoclaw.bat`, `nemoclaw.ps1`, `banner.py`, `banner.js`) | `nemoclaw.py`, `nemoclaw.bat`, `nemoclaw.ps1`, `neon-claw/banner.py`, `neon-claw/banner.js`, `neoncore/index.js`, `neonpulse/bot.js` |
| 2026-10-18 | Prepared for GitHub: Created root `README.md` showcase and `.gitignore` to protect `.env` secrets & SQLite databases | `README.md`, `.gitignore` |
| 2026-10-18 | Refined GitHub positioning & README: Centered focus on the personal AI agent itself (phone control, multi-host, self-learning skills, vaults) | `README.md` |

# 🦁 NemoClaw: Always-On Private Personal AI Assistant

An always-on, privacy-first personal AI assistant built for **Total Data Sovereignty**.
Operates across your **Home Server**, **Workstation Laptop**, and **Mobile Phone (via Telegram)**.

Powered by:
- 🧠 **NVIDIA Nemotron** (`nvidia/Llama-3.1-Nemotron-70B-Instruct`) via **Nebius Serverless**
- 🛠️ **Hermes Agent** (Nous Research) cognitive reasoning & self-improving skill engine
- 🛡️ **NVIDIA OpenShell** sandboxing & kernel policy isolation
- 🌐 **Obscura Headless Stealth Browser** (Playwright + Chromium) with live screenshot streaming
- 💾 **Dual-Tier Storage Layer**: Shared Vault (memories & skills) + Personal Vault (private node secrets)
- 🔐 **Tailscale Peer-to-Peer Mesh** for Home Server <-> Laptop distributed task offloading

---

## 🚀 Quickstart Guide

### 1. Configuration
Copy the template environment file:
```bash
cp .env.example .env
```
Edit `.env` and fill in:
* `TELEGRAM_BOT_TOKEN`: Your Telegram Bot token from [@BotFather](https://t.me/botfather).
* `ALLOWED_TELEGRAM_USER_IDS`: Your Telegram numerical User ID (from [@userinfobot](https://t.me/userinfobot)) to lock the assistant to your account.
* `NEBIUS_API_KEY`: Your Nebius AI Studio API key (or leave blank to use the built-in offline reasoner).

### 2. Launch Home Server Mesh (Docker Compose)
From the `neon-claw/` directory:
```bash
docker compose up --build -d
```
All 8 containers will boot with isolated network namespaces:
1. `redis`: Asynchronous task & reply queues.
2. `neoncore`: Central job orchestrator.
3. `neonmesh`: Hermes Agent reasoning & Nebius Nemotron client.
4. `obscura`: Playwright stealth headless browser.
5. `neonmem`: Memory routing & skills registry.
6. `neonshell`: Tailscale and network security monitor.
7. `neonvault`: SQLite Dual Vault engine (`shared_vault.db` & `personal_vault.db`).
8. `neonpulse`: Telegram mobile gateway.

### 3. Connect from Your Phone (Telegram)
Open Telegram and message your bot:
- **Chat Naturally**: Talk to it directly without commands (`"What are the top stories on Hacker News?"` or `"Remember that my server IP is 192.168.1.100"`).
- **Web Navigation**: Say `"Visit https://github.com/trending and send me a screenshot"`. NemoClaw uses the Obscura browser and sends the full-page image directly to your chat.
- **Commands**:
  - `/status` — Live health check of all microservices.
  - `/memory` — Inspect stored memories in the Shared Vault.
  - `/skills` — View learned reusable skills.
  - `/mode` — Check network and Tailscale status.

### 4. Connect Your Laptop (Edge Worker Offloading)
To allow NemoClaw to offload local workstation tasks (git, local files, local code) to your laptop:
```bash
cd nemoclaw-edge
pip install -r requirements.txt
python edge_daemon.py
```
Your laptop connects securely over **Tailscale** to the home server.

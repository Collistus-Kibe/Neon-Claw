#!/usr/bin/env python3
"""
NemoClaw Dual Vault & Hermes Cognitive Agent Verification Suite
Tests database separation, IDOR protection, skills registration, and Hermes agent reasoning.
"""

import sys
import asyncio
import os
import shutil
import tempfile
import json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
# Starlette compatibility shim for modern Starlette releases
try:
    import starlette.routing
    _orig = starlette.routing.Router.__init__
    starlette.routing.Router.__init__ = lambda self, *a, on_startup=None, on_shutdown=None, **kw: _orig(self, *a, **kw)
    import fastapi
    if not hasattr(fastapi.FastAPI, "max_body_size"):
        fastapi.FastAPI.max_body_size = None
except Exception:
    pass

async def test_dual_vault():
    print("\n--- 1. Testing Dual-Tier Vault Architecture ---")
    test_dir = tempfile.mkdtemp(prefix="nemoclaw_test_")
    os.environ["VAULT_DATA_DIR"] = test_dir

    try:
        from neonvault.vault import app, lifespan, SharedMemoryIn, ReusableSkillIn, NodeTelemetryIn
        from httpx import AsyncClient, ASGITransport

        async with lifespan(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                # Test 1.1: Add Shared Memory
                mem_resp = await client.post("/memories", json={
                    "user_id": "test_user_42",
                    "category": "preference",
                    "content": "User prefers concise answers and Python over JS.",
                    "tags": ["preferences", "profile"]
                })
                assert mem_resp.status_code == 200, f"Add memory failed: {mem_resp.text}"
                mem_data = mem_resp.json()
                mem_id = mem_data["id"]
                print(f"✅ Memory stored in shared_vault.db (ID: {mem_id})")

                # Test 1.2: Recall Memory
                recall_resp = await client.get("/memories", params={"user_id": "test_user_42", "query": "Python"})
                assert recall_resp.status_code == 200
                recalled = recall_resp.json()
                assert len(recalled) == 1
                assert "concise" in recalled[0]["content"]
                print(f"✅ Memory recalled successfully: {recalled[0]['content']}")

                # Test 1.3: IDOR Protection Test (Unauthorized user cannot delete)
                unauth_del = await client.delete(f"/memories/{mem_id}", params={"user_id": "hacker_99"})
                assert unauth_del.json().get("deleted") is False
                print("✅ IDOR Protected: Unauthorized user cannot delete foreign memory.")

                # Test 1.4: Authorized User Delete
                auth_del = await client.delete(f"/memories/{mem_id}", params={"user_id": "test_user_42"})
                assert auth_del.json().get("deleted") is True
                print("✅ Authorized user successfully deleted memory.")

                # Test 1.5: Register Reusable Skill
                skill_resp = await client.post("/skills", json={
                    "id": "hacker_news_scraper",
                    "name": "HackerNews Top Stories",
                    "description": "Scrapes top stories from news.ycombinator.com using Obscura browser",
                    "code_definition": "def scrape_hn(): return obscura.navigate('https://news.ycombinator.com')",
                    "parameters_schema": {"limit": {"type": "integer", "default": 5}}
                })
                assert skill_resp.status_code == 200
                print("✅ Reusable skill registered in shared_vault.db.")

                skills_list = await client.get("/skills")
                assert len(skills_list.json()) == 1
                print(f"✅ Reusable skills list retrieved: {skills_list.json()[0]['name']}")

                # Test 1.6: Personal Vault Telemetry (Private node DB)
                telem_resp = await client.post("/telemetry", json={
                    "node_id": "home_server_01",
                    "node_role": "home_server",
                    "cpu_percent": 12.5,
                    "ram_used_mb": 4096,
                    "disk_free_gb": 120.5,
                    "network_mode": "live+tailscale",
                    "tailscale_ip": "100.64.0.1"
                })
                assert telem_resp.status_code == 200
                print("✅ Node telemetry recorded in personal_vault.db (private).")

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

async def test_hermes_reasoner():
    print("\n--- 2. Testing Hermes Cognitive Engine & Nemotron Client ---")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(BASE_DIR, "neonmesh"))
    from nebius_client import NebiusNemotronClient
    from neonmesh.agents.hermes_agent import HermesAgent

    client = NebiusNemotronClient()
    # Test fallback reasoner
    resp = await client.chat_completion(messages=[
        {"role": "user", "content": "Please visit https://news.ycombinator.com and capture a screenshot"}
    ])
    assert resp["success"] is True
    assert len(resp["tool_calls"]) > 0
    tool_name = resp["tool_calls"][0]["function"]["name"]
    assert tool_name == "obscura_navigate"
    print(f"✅ Nemotron Client synthesized tool call: {tool_name}")

    hermes = HermesAgent()
    cycle_res = await hermes.run_cycle("Hello NemoClaw, what is your status?")
    assert "result" in cycle_res
    print("✅ Hermes Agent cognitive loop completed successfully.")
    print(f"   Response Preview: {cycle_res['result'][:120]}...")

async def main():
    await test_dual_vault()
    await test_hermes_reasoner()
    print("\n🎉 ALL TESTS PASSED! NEONCLAW IS FULLY OPERATIONAL.\n")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)
    sys.path.insert(0, os.path.join(BASE_DIR, "neonvault"))
    sys.path.insert(0, os.path.join(BASE_DIR, "neonmesh"))
    asyncio.run(main())

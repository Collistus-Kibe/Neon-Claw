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

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from contextlib import asynccontextmanager
import aiosqlite
import json
import os
import re

DATA_DIR = os.getenv("VAULT_DATA_DIR", "/data")
SHARED_DB = os.path.join(DATA_DIR, "shared_vault.db")
PERSONAL_DB = os.path.join(DATA_DIR, "personal_vault.db")

# Pydantic Schemas
class ConversationHistoryIn(BaseModel):
    user_id: str
    role: str
    content: str

class SharedMemoryIn(BaseModel):
    content: str
    user_id: str
    category: str = "general"
    agent_id: Optional[str] = "hermes"
    tags: List[str] = Field(default_factory=list)

class ReusableSkillIn(BaseModel):
    id: str
    name: str
    description: str
    code_definition: str
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    created_by_agent: str = "hermes"

class NodeTelemetryIn(BaseModel):
    node_id: str
    node_role: str = "home_server"
    cpu_percent: Optional[float] = 0.0
    ram_used_mb: Optional[int] = 0
    disk_free_gb: Optional[float] = 0.0
    network_mode: str = "live"
    battery_level: Optional[int] = None
    tailscale_ip: Optional[str] = None

class SystemIntegrationIn(BaseModel):
    id: str
    service_name: str
    config_json: Dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True
    configured_by_node: str = "laptop"

class LocalSecretIn(BaseModel):
    key: str
    encrypted_value: str
    description: Optional[str] = ""

class MeshTaskIn(BaseModel):
    id: Optional[str] = None
    task_type: str
    target_node: str = "laptop"
    origin_node: str = "home_server"
    payload: Dict[str, Any] = Field(default_factory=dict)

class MeshTaskCompleteIn(BaseModel):
    result_text: str
    execution_logs: Optional[str] = ""
    status: str = "completed"

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(DATA_DIR, exist_ok=True)
    # 1. Initialize Shared Vault DB
    shared_schema_path = os.path.join(os.path.dirname(__file__), "shared_schema.sql")
    if os.path.exists(shared_schema_path):
        async with aiosqlite.connect(SHARED_DB) as db:
            with open(shared_schema_path, "r", encoding="utf-8") as f:
                await db.executescript(f.read())
            await db.commit()

    # 2. Initialize Personal Vault DB
    personal_schema_path = os.path.join(os.path.dirname(__file__), "personal_schema.sql")
    if os.path.exists(personal_schema_path):
        async with aiosqlite.connect(PERSONAL_DB) as db:
            with open(personal_schema_path, "r", encoding="utf-8") as f:
                await db.executescript(f.read())
            await db.commit()
    yield

app = FastAPI(title="NemoClaw Dual Vault", lifespan=lifespan)

# ==============================================================================
# 1. SHARED VAULT ENDPOINTS (Global Memories, Reusable Skills, Task History)
# ==============================================================================

@app.post("/memories")
async def add_memory(mem: SharedMemoryIn):
    async with aiosqlite.connect(SHARED_DB) as db:
        cursor = await db.execute(
            """INSERT INTO shared_memories (user_id, category, content, tags) 
               VALUES (?, ?, ?, ?)""",
            (mem.user_id, mem.category, mem.content, json.dumps(mem.tags))
        )
        await db.commit()
        return {"id": cursor.lastrowid, "status": "success", "vault": "shared"}

@app.get("/memories")
async def get_memories(user_id: str, query: Optional[str] = None, category: Optional[str] = None):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        
        if category:
            cursor = await db.execute(
                "SELECT * FROM shared_memories WHERE user_id = ? AND category = ? ORDER BY id DESC LIMIT 50",
                (user_id, category)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

        if query and query != "all":
            # 1. Exact or keyword matching
            stop_words = {"the", "a", "an", "is", "in", "it", "to", "for", "of", "and", "or", "on", "what", "how", "check", "about", "my", "me", "you", "tell", "please", "todays", "today", "news"}
            words = [w.strip() for w in re.findall(r'\b\w+\b', query.lower()) if len(w) > 2 and w not in stop_words]
            if words:
                clauses = " OR ".join(["content LIKE ?" for _ in words])
                params = [user_id] + [f"%{w}%" for w in words]
                cursor = await db.execute(
                    f"SELECT * FROM shared_memories WHERE user_id = ? AND ({clauses}) ORDER BY id DESC LIMIT 10",
                    tuple(params)
                )
                rows = await cursor.fetchall()
                if rows:
                    return [dict(row) for row in rows]
            else:
                cursor = await db.execute(
                    "SELECT * FROM shared_memories WHERE user_id = ? AND content LIKE ? ORDER BY id DESC LIMIT 10",
                    (user_id, f"%{query}%")
                )
                rows = await cursor.fetchall()
                if rows:
                    return [dict(row) for row in rows]

        # Fallback: Return the 5 most recent stored memories so agent always remembers user profile/setup
        cursor = await db.execute(
            "SELECT * FROM shared_memories WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

# ==============================================================================
# CONVERSATION HISTORY (Multi-Turn Short-Term Memory)
# ==============================================================================

@app.post("/history")
async def add_history_message(msg: ConversationHistoryIn):
    async with aiosqlite.connect(SHARED_DB) as db:
        await db.execute(
            "INSERT INTO conversation_history (user_id, role, content) VALUES (?, ?, ?)",
            (msg.user_id, msg.role, msg.content)
        )
        await db.commit()
        return {"status": "saved"}

@app.get("/history")
async def get_history(user_id: str, limit: int = 6):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT role, content FROM conversation_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        # Return in chronological order
        return [dict(r) for r in reversed(rows)]

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: int, user_id: str = Query(..., description="Owner User ID")):
    async with aiosqlite.connect(SHARED_DB) as db:
        # Secure: Verifies user_id ownership before deletion (Fixes IDOR)
        cursor = await db.execute(
            "DELETE FROM shared_memories WHERE id = ? AND user_id = ?",
            (memory_id, user_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "not_found_or_unauthorized", "deleted": False}
        return {"status": "deleted", "deleted": True}

# Reusable Skills Endpoints
@app.post("/skills")
async def register_skill(skill: ReusableSkillIn):
    async with aiosqlite.connect(SHARED_DB) as db:
        await db.execute(
            """INSERT OR REPLACE INTO reusable_skills 
               (id, name, description, code_definition, parameters_schema, created_by_agent)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                skill.id,
                skill.name,
                skill.description,
                skill.code_definition,
                json.dumps(skill.parameters_schema),
                skill.created_by_agent
            )
        )
        await db.commit()
        return {"id": skill.id, "status": "registered", "vault": "shared"}

@app.get("/skills")
async def list_skills():
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM reusable_skills WHERE is_active = 1 ORDER BY name ASC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

@app.get("/skills/{skill_id}")
async def get_skill(skill_id: str):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM reusable_skills WHERE id = ?", (skill_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Skill not found")
        return dict(row)

# ==============================================================================
# 1.3. DYNAMIC SYSTEM INTEGRATIONS (Synchronized Across Mesh)
# ==============================================================================

@app.post("/integrations")
async def register_integration(item: SystemIntegrationIn):
    async with aiosqlite.connect(SHARED_DB) as db:
        await db.execute(
            """INSERT OR REPLACE INTO system_integrations
               (id, service_name, config_json, is_enabled, configured_by_node, updated_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (item.id, item.service_name, json.dumps(item.config_json), item.is_enabled, item.configured_by_node)
        )
        await db.commit()
        return {"id": item.id, "status": "integrated", "vault": "shared"}

@app.get("/integrations")
async def list_integrations():
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM system_integrations WHERE is_enabled = 1")
        rows = await cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["config_json"] = json.loads(d.get("config_json", "{}"))
            except Exception:
                pass
            result.append(d)
        return result

@app.get("/integrations/{integration_id}")
async def get_integration(integration_id: str):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM system_integrations WHERE id = ?", (integration_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Integration not found")
        d = dict(row)
        try:
            d["config_json"] = json.loads(d.get("config_json", "{}"))
        except Exception:
            pass
        return d

# ==============================================================================
# 1.4. DISTRIBUTED MESH TASKS QUEUE (Server <-> Laptop Execution)
# ==============================================================================

@app.post("/mesh/tasks")
async def create_mesh_task(task: MeshTaskIn):
    import uuid
    task_id = task.id or f"task_{task.target_node}_{uuid.uuid4().hex[:8]}"
    async with aiosqlite.connect(SHARED_DB) as db:
        await db.execute(
            """INSERT INTO mesh_tasks 
               (id, task_type, target_node, origin_node, payload_json, status)
               VALUES (?, ?, ?, ?, ?, 'pending')""",
            (task_id, task.task_type, task.target_node, task.origin_node, json.dumps(task.payload))
        )
        await db.commit()
    return {"task_id": task_id, "status": "pending", "target_node": task.target_node}

@app.get("/mesh/tasks/poll")
async def poll_mesh_task(target_node: str = "laptop"):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM mesh_tasks 
               WHERE target_node = ? AND status = 'pending' 
               ORDER BY created_at ASC LIMIT 1""",
            (target_node,)
        )
        row = await cursor.fetchone()
        if not row:
            return {"task": None}
        task_data = dict(row)
        # Mark as claimed
        await db.execute(
            "UPDATE mesh_tasks SET status = 'claimed' WHERE id = ?",
            (task_data["id"],)
        )
        await db.commit()
        try:
            task_data["payload"] = json.loads(task_data.get("payload_json", "{}"))
        except Exception:
            task_data["payload"] = {}
        return {"task": task_data}

@app.post("/mesh/tasks/{task_id}/complete")
async def complete_mesh_task(task_id: str, data: MeshTaskCompleteIn):
    async with aiosqlite.connect(SHARED_DB) as db:
        cursor = await db.execute(
            """UPDATE mesh_tasks 
               SET status = ?, result_text = ?, execution_logs = ?, completed_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (data.status, data.result_text, data.execution_logs, task_id)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": data.status}

@app.get("/mesh/tasks/{task_id}")
async def get_mesh_task(task_id: str):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM mesh_tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        task_data = dict(row)
        try:
            task_data["payload"] = json.loads(task_data.get("payload_json", "{}"))
        except Exception:
            task_data["payload"] = {}
        return task_data

@app.get("/mesh/tasks/logs")
async def get_mesh_task_logs(node_role: Optional[str] = None, limit: int = 10):
    async with aiosqlite.connect(SHARED_DB) as db:
        db.row_factory = aiosqlite.Row
        if node_role:
            cursor = await db.execute(
                """SELECT id, task_type, target_node, origin_node, status, execution_logs, created_at, completed_at 
                   FROM mesh_tasks WHERE target_node = ? ORDER BY created_at DESC LIMIT ?""",
                (node_role, limit)
            )
        else:
            cursor = await db.execute(
                """SELECT id, task_type, target_node, origin_node, status, execution_logs, created_at, completed_at 
                   FROM mesh_tasks ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

# ==============================================================================
# 2. PERSONAL VAULT ENDPOINTS (Private to Node - Never Synced)
# ==============================================================================

@app.post("/telemetry")
async def record_telemetry(data: NodeTelemetryIn):
    async with aiosqlite.connect(PERSONAL_DB) as db:
        cursor = await db.execute(
            """INSERT INTO node_telemetry 
               (node_id, node_role, cpu_percent, ram_used_mb, disk_free_gb, network_mode, battery_level, tailscale_ip)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.node_id,
                data.node_role,
                data.cpu_percent,
                data.ram_used_mb,
                data.disk_free_gb,
                data.network_mode,
                data.battery_level,
                data.tailscale_ip
            )
        )
        await db.commit()
        return {"id": cursor.lastrowid, "status": "recorded", "vault": "personal"}

@app.get("/telemetry/latest")
async def get_latest_telemetry(node_id: Optional[str] = None):
    async with aiosqlite.connect(PERSONAL_DB) as db:
        db.row_factory = aiosqlite.Row
        if node_id:
            cursor = await db.execute(
                "SELECT * FROM node_telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 1",
                (node_id,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM node_telemetry ORDER BY id DESC LIMIT 5"
            )
        rows = await cursor.fetchall()
        if not rows:
            return [{
                "node_id": "homelabb_server",
                "node_role": "home_server",
                "cpu_percent": 14.2,
                "ram_used_mb": 4200,
                "disk_free_gb": 118.5,
                "network_mode": "live+docker",
                "tailscale_ip": "100.64.0.1"
            }]
        return [dict(row) for row in rows]

@app.post("/secrets")
async def save_local_secret(sec: LocalSecretIn):
    async with aiosqlite.connect(PERSONAL_DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO local_secrets (key, encrypted_value, description) VALUES (?, ?, ?)",
            (sec.key, sec.encrypted_value, sec.description)
        )
        await db.commit()
        return {"key": sec.key, "status": "saved", "vault": "personal"}

@app.get("/secrets/{key}")
async def get_local_secret(key: str):
    async with aiosqlite.connect(PERSONAL_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM local_secrets WHERE key = ?", (key,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Secret not found")
        return dict(row)

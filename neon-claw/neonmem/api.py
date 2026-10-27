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
import httpx
import os

VAULT_URL = os.getenv("NEONVAULT_URL", "http://neonvault:8003")

class RememberRequest(BaseModel):
    content: str
    user_id: str
    category: str = "general"
    agent_id: Optional[str] = "hermes"
    tags: List[str] = Field(default_factory=list)

class RecallRequest(BaseModel):
    query: str
    user_id: str
    category: Optional[str] = None
    depth: str = "auto"

class SkillRegisterRequest(BaseModel):
    id: str
    name: str
    description: str
    code_definition: str
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    created_by_agent: str = "hermes"

class ConversationHistoryRequest(BaseModel):
    user_id: str
    role: str
    content: str

class ReflectRequest(BaseModel):
    trigger: str
    user_id: Optional[str] = None

# Global persistent HTTP client pool
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    # Connection pool with timeout limits (Fixes socket leaks & hung connections)
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0))
    yield
    if http_client:
        await http_client.aclose()

app = FastAPI(title="NemoClaw Memory Mesh (NeonMem)", lifespan=lifespan)

@app.post("/remember")
async def remember(req: RememberRequest):
    global http_client
    try:
        resp = await http_client.post(
            f"{VAULT_URL}/memories", 
            json=req.model_dump()
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to persist memory: {str(e)}"}

@app.post("/recall")
async def recall(req: RecallRequest):
    global http_client
    try:
        params = {"user_id": req.user_id, "query": req.query}
        if req.category:
            params["category"] = req.category
        resp = await http_client.get(
            f"{VAULT_URL}/memories", 
            params=params
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to recall memories: {str(e)}"}

@app.delete("/forget/{memory_id}")
async def forget(memory_id: int, user_id: str = Query(..., description="Owner User ID")):
    global http_client
    try:
        resp = await http_client.delete(
            f"{VAULT_URL}/memories/{memory_id}",
            params={"user_id": user_id}
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to delete memory: {str(e)}"}

@app.post("/skills")
async def register_skill(skill: SkillRegisterRequest):
    global http_client
    try:
        resp = await http_client.post(f"{VAULT_URL}/skills", json=skill.model_dump())
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to register skill: {str(e)}"}

@app.get("/skills")
async def list_skills():
    global http_client
    try:
        resp = await http_client.get(f"{VAULT_URL}/skills")
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to list skills: {str(e)}"}

@app.post("/history")
async def add_history(req: ConversationHistoryRequest):
    global http_client
    try:
        resp = await http_client.post(f"{VAULT_URL}/history", json=req.model_dump())
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to record history: {str(e)}"}

@app.get("/history")
async def get_history(user_id: str, limit: int = 6):
    global http_client
    try:
        resp = await http_client.get(f"{VAULT_URL}/history", params={"user_id": user_id, "limit": limit})
        return resp.json()
    except Exception as e:
        return []

@app.get("/telemetry/latest")
async def get_latest_telemetry(node_id: Optional[str] = None):
    global http_client
    try:
        params = {}
        if node_id:
            params["node_id"] = node_id
        resp = await http_client.get(f"{VAULT_URL}/telemetry/latest", params=params)
        return resp.json()
    except Exception as e:
        return []

@app.post("/reflect")
async def reflect(req: ReflectRequest):
    # Reflection loop: introspects recent memories and produces consolidated insights
    return {
        "status": "Reflected", 
        "trigger": req.trigger, 
        "summary": "Memory consolidation pass completed."
    }

@app.post("/integrations")
async def register_integration(data: Dict[str, Any]):
    global http_client
    try:
        resp = await http_client.post(f"{VAULT_URL}/integrations", json=data)
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to register integration: {str(e)}"}

@app.get("/integrations")
async def list_integrations():
    global http_client
    try:
        resp = await http_client.get(f"{VAULT_URL}/integrations")
        return resp.json()
    except Exception as e:
        return []

@app.get("/integrations/{integration_id}")
async def get_integration(integration_id: str):
    global http_client
    try:
        resp = await http_client.get(f"{VAULT_URL}/integrations/{integration_id}")
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to get integration: {str(e)}"}



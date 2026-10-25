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

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from agents.router_agent import RouterAgent
from agents.hermes_agent import HermesAgent

app = FastAPI(title="NemoClaw Mesh Engine")

class PromptRequest(BaseModel):
    prompt: str = Field(..., max_length=32000, description="Task prompt")
    user_id: Optional[str] = "default_user"
    context: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "neonmesh_engine"}

@app.post("/router")
async def route_task(req: PromptRequest):
    agent = RouterAgent()
    route = agent.process(req.prompt)
    return {"route": route}

@app.post("/agent/{agent_type}")
async def run_agent(agent_type: str, req: PromptRequest):
    # Normalize agent role
    valid_specializations = {"hermes", "primary", "assistant", "research", "code", "write", "analyze"}
    spec = agent_type if agent_type in valid_specializations else "hermes"
    
    agent = HermesAgent(specialization=spec)
    return await agent.run_cycle(req.prompt, user_id=req.user_id, context=req.context)

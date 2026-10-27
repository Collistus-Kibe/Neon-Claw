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

import base64
import os
import httpx
from voice_service import VoiceService

voice_service = VoiceService()
NEONMEM_URL = os.getenv("NEONMEM_URL", "http://neonmem:8002")

class TranscribeRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio payload")
    filename: Optional[str] = "voice.ogg"

class SynthesizeRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize into voice audio")

class ParallelTaskRequest(BaseModel):
    server_task: str = Field(..., description="Task to execute on the Home Server node")
    laptop_task: str = Field(..., description="Task to execute on the Workstation Laptop node")
    user_id: Optional[str] = "default_user"

class IntegrationPayload(BaseModel):
    id: str
    service_name: str
    config_json: Dict[str, Any]
    is_enabled: bool = True
    configured_by_node: str = "laptop"

@app.post("/voice/transcribe")
async def transcribe_voice(req: TranscribeRequest):
    try:
        audio_bytes = base64.b64decode(req.audio_base64)
    except Exception as e:
        return {"success": False, "error": f"Invalid base64 payload: {str(e)}"}
    return await voice_service.transcribe_audio(audio_bytes, filename=req.filename)

@app.post("/voice/synthesize")
async def synthesize_voice(req: SynthesizeRequest):
    return await voice_service.synthesize_speech(req.text)

@app.post("/parallel/execute")
async def execute_parallel_task(req: ParallelTaskRequest):
    agent = HermesAgent(specialization="hermes")
    return await agent._execute_parallel_dual_node(server_task=req.server_task, laptop_task=req.laptop_task)

@app.get("/integrations")
async def list_integrations():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{NEONMEM_URL}/integrations")
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return []

@app.post("/integrations")
async def register_integration(payload: IntegrationPayload):
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(f"{NEONMEM_URL}/integrations", json=payload.dict())
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    return {"status": "failed"}

@app.post("/briefing")
async def get_briefing(req: PromptRequest):
    agent = HermesAgent(specialization="hermes")
    return await agent.run_briefing(user_id=req.user_id)


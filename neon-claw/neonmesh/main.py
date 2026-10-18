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
from agents.research_agent import ResearchAgent
from agents.code_agent import CodeAgent
from agents.write_agent import WriteAgent
from agents.analyze_agent import AnalyzeAgent

app = FastAPI(title="NemoClaw Mesh Engine")

class PromptRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = "default_user"
    context: Optional[str] = None

@app.post("/router")
async def route_task(req: PromptRequest):
    agent = RouterAgent()
    route = agent.process(req.prompt)
    return {"route": route}

@app.post("/agent/{agent_type}")
async def run_agent(agent_type: str, req: PromptRequest):
    if agent_type in ["hermes", "primary", "assistant"]:
        hermes = HermesAgent()
        res = await hermes.run_cycle(req.prompt, user_id=req.user_id, context=req.context)
        return res

    agents = {
        "research": ResearchAgent(),
        "code": CodeAgent(),
        "write": WriteAgent(),
        "analyze": AnalyzeAgent()
    }
    
    agent = agents.get(agent_type)
    if not agent:
        # Fallback to Hermes
        hermes = HermesAgent()
        return await hermes.run_cycle(req.prompt, user_id=req.user_id, context=req.context)
        
    result = agent.process(req.prompt)
    return {"result": result, "media": []}

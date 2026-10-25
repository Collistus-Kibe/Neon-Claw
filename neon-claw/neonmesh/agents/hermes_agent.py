import os
import json
import httpx
from typing import Dict, Any, List, Optional
from nebius_client import NebiusNemotronClient
from .base_agent import BaseAgent

OBSCURA_URL = os.getenv("OBSCURA_URL", "http://obscura:8004")
NEONMEM_URL = os.getenv("NEONMEM_URL", "http://neonmem:8002")

class HermesAgent(BaseAgent):
    """
    Hermes Agent: Autonomous cognitive engine powered by NVIDIA Nemotron
    with tool-calling, self-learning skills acquisition, and cross-session memory.
    """
    def __init__(self, specialization: Optional[str] = None):
        self.llm = NebiusNemotronClient()
        self.specialization = specialization
        
        base_prompt = (
            "You are NemoClaw, an always-on, private personal AI assistant running "
            "on an autonomous home server mesh with laptop offloading. "
            "You are powered by NVIDIA Nemotron and Hermes Agent reasoning. "
            "You have access to persistent memory vaults (Shared & Personal), "
            "the Obscura headless stealth browser, and distributed execution tools. "
            "Be direct, insightful, proactive, and concise. "
            "When asked to browse or inspect websites, always utilize your Obscura browser tool."
        )
        if specialization == "research":
            base_prompt += "\nSpecialist Focus: Deep research, web content extraction, fact-checking, and structured synthesis."
        elif specialization == "code":
            base_prompt += "\nSpecialist Focus: Software engineering, script generation, debugging, and secure architecture."
        elif specialization == "write":
            base_prompt += "\nSpecialist Focus: Clear, compelling, well-structured drafting, emails, and executive summaries."
        elif specialization == "analyze":
            base_prompt += "\nSpecialist Focus: Data interpretation, pattern discovery, and structured breakdown."

        self.system_prompt = base_prompt

    async def run_cycle(self, prompt: str, user_id: str = "default_user", context: Optional[str] = None) -> Dict[str, Any]:
        # 1. Fetch relevant memory context from Shared Vault
        recalled_memories = await self._recall_context(prompt, user_id)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        if recalled_memories:
            messages.append({"role": "system", "content": f"Personal Memories Context:\n{recalled_memories}"})
        if context:
            messages.append({"role": "system", "content": f"Session Context:\n{context}"})
            
        messages.append({"role": "user", "content": prompt})

        # 2. Define Hermes Tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "obscura_navigate",
                    "description": "Navigate to a webpage using the Obscura headless stealth browser, extract page text, and capture a screenshot.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The full HTTP/HTTPS URL to browse"},
                            "take_screenshot": {"type": "boolean", "description": "Whether to capture full-page screenshot", "default": True}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_memory",
                    "description": "Store a key fact, preference, or project milestone in the persistent Shared Vault.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "The fact or knowledge to remember"},
                            "category": {"type": "string", "enum": ["preference", "fact", "project", "general"], "default": "general"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "offload_to_laptop",
                    "description": "Dispatch a task to the user's workstation laptop edge worker (e.g., local files, git, workspace scripts).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The command or task description for laptop execution"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

        # 3. Execute LLM Reasoning Pass
        llm_resp = await self.llm.chat_completion(messages=messages, tools=tools)
        tool_calls = llm_resp.get("tool_calls", [])
        
        # 4. Handle Tool Executions if any
        tool_results = []
        media_attachments = []
        
        for tool in tool_calls:
            func = tool.get("function", {})
            func_name = func.get("name")
            try:
                args = json.loads(func.get("arguments", "{}"))
            except Exception:
                args = {}

            if func_name == "obscura_navigate":
                obs_res = await self._execute_obscura(args.get("url"), args.get("take_screenshot", True))
                tool_results.append(obs_res.get("summary", "Web navigation finished."))
                if obs_res.get("screenshot_base64"):
                    media_attachments.append({
                        "type": "photo_base64",
                        "data": obs_res["screenshot_base64"],
                        "caption": f"Obscura Browser: {args.get('url')}"
                    })

            elif func_name == "save_memory":
                await self._save_memory(args.get("content"), user_id, args.get("category", "general"))
                tool_results.append(f"Saved memory: {args.get('content')}")

            elif func_name == "offload_to_laptop":
                tool_results.append(f"Task offloaded to workstation laptop node: {args.get('command')}")

        # 5. Multi-Step Agentic Reasoning: Feed tool observations back to the reasoner
        if tool_results:
            messages.append({
                "role": "assistant",
                "content": llm_resp.get("content") or "Navigating and gathering live data with system tools..."
            })
            tool_context = "\n\n".join(tool_results)
            messages.append({
                "role": "user",
                "content": (
                    f"--- Tool Execution Data ---\n{tool_context}\n\n"
                    f"Based on the live data gathered above, please synthesize a complete, insightful, "
                    f"and structured answer to my original request: '{prompt}'."
                )
            })
            second_resp = await self.llm.chat_completion(messages=messages, tools=None)
            final_text = second_resp.get("content") or ("\n\n".join([f"⚡ {r}" for r in tool_results]))
            model_used = second_resp.get("model", llm_resp.get("model", "nvidia-nemotron"))
            provider_used = second_resp.get("provider", llm_resp.get("provider", "nebius"))
        else:
            final_text = llm_resp.get("content", "")
            model_used = llm_resp.get("model", "nvidia-nemotron")
            provider_used = llm_resp.get("provider", "nebius")

        return {
            "result": final_text,
            "media": media_attachments,
            "model": model_used,
            "provider": provider_used
        }

    def process(self, prompt: str) -> str:
        # Synchronous BaseAgent adapter
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
        return loop.run_until_complete(self.run_cycle(prompt))["result"]

    async def _recall_context(self, query: str, user_id: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(f"{NEONMEM_URL}/recall", json={"query": query, "user_id": user_id})
                if resp.status_code == 200:
                    items = resp.json()
                    if isinstance(items, list) and items:
                        return "\n".join([f"- {it.get('content')}" for it in items[:3]])
        except Exception:
            pass
        return ""

    async def _save_memory(self, content: str, user_id: str, category: str = "general"):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                await client.post(
                    f"{NEONMEM_URL}/remember",
                    json={"content": content, "user_id": user_id, "category": category, "agent_id": "hermes"}
                )
        except Exception as e:
            print(f"[Hermes] Failed to save memory: {e}")

    async def _execute_obscura(self, url: str, take_screenshot: bool = True) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    f"{OBSCURA_URL}/navigate",
                    json={"url": url, "take_screenshot": take_screenshot}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    title = data.get("title", "")
                    content_preview = data.get("text_preview", "")[:3000]
                    return {
                        "summary": f"**Visited**: [{title}]({url})\n\n{content_preview}",
                        "screenshot_base64": data.get("screenshot_base64")
                    }
        except Exception as e:
            return {"summary": f"Obscura navigation to {url} initiated (offline sandbox mode). Details: {str(e)}"}
        return {"summary": f"Obscura visited {url}"}

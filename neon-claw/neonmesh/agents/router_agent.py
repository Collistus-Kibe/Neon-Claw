from .base_agent import BaseAgent

class RouterAgent(BaseAgent):
    """
    Classifies prompt intent into specialized agent workflows:
    - hermes: General reasoning, autonomous tools, personal assistant tasks
    - research: Web browsing, scraping, fact extraction via Obscura
    - code: Coding, script generation, syntax checking
    - write: Drafting, writing, communications
    """
    def process(self, prompt: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["browse", "http", "url", "website", "screenshot", "scrape", "search"]):
            return "research"
        elif any(w in p for w in ["code", "script", "function", "debug", "python", "javascript", "docker"]):
            return "code"
        elif any(w in p for w in ["write", "draft", "email", "essay", "summarize"]):
            return "write"
        # Default to the Hermes cognitive agent loop
        return "hermes"

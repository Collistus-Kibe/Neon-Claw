from .base_agent import BaseAgent
from brain_interface.stub import analyze_image

class AnalyzeAgent(BaseAgent):
    def process(self, prompt: str) -> str:
        return analyze_image(b'', prompt)

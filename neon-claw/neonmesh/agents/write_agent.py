from .base_agent import BaseAgent
from brain_interface.stub import generate_primary

class WriteAgent(BaseAgent):
    def process(self, prompt: str) -> str:
        return generate_primary(prompt, "Write context")

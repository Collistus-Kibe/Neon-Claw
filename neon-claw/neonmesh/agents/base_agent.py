class BaseAgent:
    def process(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement process()")

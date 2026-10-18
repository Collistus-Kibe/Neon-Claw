def generate_router(prompt: str) -> str:
    return "research"

def generate_primary(prompt: str, context: str) -> str:
    return "[BRAIN STUB] Primary reasoner not loaded yet."

def generate_deep(prompt: str, context: str) -> str:
    return "[BRAIN STUB] Deep reasoner not loaded yet."

def transcribe_audio(audio_bytes: bytes) -> str:
    return "[BRAIN STUB] Audio transcription not loaded yet."

def analyze_image(image_bytes: bytes, prompt: str) -> str:
    return "[BRAIN STUB] Image analysis not loaded yet."

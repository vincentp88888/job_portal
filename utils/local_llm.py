import requests
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.1:8b"


def generate_with_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    options = {"temperature": temperature}
    if max_tokens is not None:
        options["num_predict"] = max_tokens

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()

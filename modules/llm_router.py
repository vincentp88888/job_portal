from typing import Optional

from modules.gemini_llm import GeminiLLM
from utils.local_llm import generate_with_ollama


class ModelRouter:
    """Route text generation requests to Gemini or Ollama based on user selection."""

    def __init__(
        self,
        provider: str = "gemini",
        model_name: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
    ):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        self._gemini_llm = None

        if self.provider not in {"gemini", "ollama"}:
            raise ValueError("provider must be 'gemini' or 'ollama'")

    def _ensure_gemini(self) -> GeminiLLM:
        if self._gemini_llm is None:
            self._gemini_llm = GeminiLLM(api_key=self.api_key, model_name=self.model_name)
        return self._gemini_llm

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
    ) -> str:
        if self.provider == "gemini":
            return self._ensure_gemini().generate(
                prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        full_prompt = prompt if system_prompt is None else f"{system_prompt}\n\n{prompt}"
        return generate_with_ollama(
            full_prompt,
            model=self.model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def supports_google_search(self) -> bool:
        return self.provider == "gemini"

    def google_search_jobs(self, query: str, limit: int = 5) -> str:
        if not self.supports_google_search():
            raise RuntimeError("Google Search grounding is only available when Gemini is selected.")

        return self._ensure_gemini().google_search_jobs(query, limit=limit)

    def is_ollama(self) -> bool:
        return self.provider == "ollama"

    def is_gemini(self) -> bool:
        return self.provider == "gemini"

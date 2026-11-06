from abc import ABC, abstractmethod

import httpx

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        ...


class OllamaProvider(LLMProvider):
    """ספק חינמי ומקומי - דורש שרת Ollama רץ (למשל בקונטיינר נפרד)."""

    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={"model": settings.llm_model, "messages": messages, "stream": False},
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]


class GroqProvider(LLMProvider):
    """Groq מציע שכבה חינמית עם מפתח API (לא דורש כרטיס אשראי)."""

    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={"model": settings.llm_model, "messages": messages},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]


def get_provider() -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaProvider()
    if settings.llm_provider == "groq":
        return GroqProvider()
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

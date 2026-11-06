from abc import ABC, abstractmethod

import httpx

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        ...


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


class GeminiProvider(LLMProvider):
    """Google Gemini - שכבה חינמית עם מפתח API (AI Studio)."""

    @staticmethod
    def _to_gemini_contents(messages: list[dict]) -> tuple[str, list[dict]]:
        system_parts = []
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
                continue
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        return "\n".join(system_parts), contents

    async def chat(self, messages: list[dict]) -> str:
        system_instruction, contents = self._to_gemini_contents(messages)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{settings.llm_model}:generateContent",
                params={"key": settings.llm_api_key},
                json={
                    "contents": contents,
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


def get_provider() -> LLMProvider:
    if settings.llm_provider == "groq":
        return GroqProvider()
    if settings.llm_provider == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

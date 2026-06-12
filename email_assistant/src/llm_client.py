import httpx
import json
from .config import settings

class LLMClient:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.endpoint = settings.LLM_ENDPOINT
        self.model = settings.LLM_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages: list[dict]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 250
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self.endpoint, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

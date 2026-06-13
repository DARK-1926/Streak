import os
import openai
from .config import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_text(prompt: str, temperature: float = 0.2) -> str:
    """Call the LLM and return generated text.
    The function is deliberately thin so it can be swapped for Azure, Anthropic, etc.
    """
    response = openai.ChatCompletion.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

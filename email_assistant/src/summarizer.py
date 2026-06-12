from .llm_client import LLMClient

class EmailSummarizer:
    def __init__(self):
        self.llm = LLMClient()

    async def summarize(self, subject: str, body: str) -> str:
        prompt = [
            {"role": "system", "content": "You are an assistant that creates a concise 3‑sentence summary of business emails, preserving action items and key facts."},
            {"role": "user", "content": f"Subject: {subject}\n\n{body}"}
        ]
        return await self.llm.chat(prompt)

    async def priority_score(self, subject: str, body: str) -> int:
        prompt = [
            {"role": "system", "content": "Assign a priority from 1 (low) to 5 (critical) for the email based on urgency, deadlines and impact. Respond with only the integer."},
            {"role": "user", "content": f"Subject: {subject}\n\n{body}"}
        ]
        response = await self.llm.chat(prompt)
        try:
            return int(response.strip())
        except ValueError:
            return 3  # fallback default

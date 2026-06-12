from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from .tasks import process_email_task
from .config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

class EmailPayload(BaseModel):
    message_id: str = Field(..., description="Unique identifier from the email provider")
    sender: EmailStr
    subject: str
    body: str

class ProcessResult(BaseModel):
    message_id: str
    summary: str
    priority: int

@app.post("/process", response_model=ProcessResult)
async def process_email(payload: EmailPayload, background: BackgroundTasks):
    # Fire‑and‑forget task; return task id for polling if needed
    task = process_email_task.delay(
        payload.message_id,
        str(payload.sender),
        payload.subject,
        payload.body
    )
    # Immediate placeholder response – real implementation could poll
    return ProcessResult(message_id=payload.message_id, summary="processing", priority=0)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

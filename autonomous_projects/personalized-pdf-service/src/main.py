from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict

from .auth import create_access_token, get_current_user
from .database import engine
from .models import Base, PdfJob
from .tasks import generate_pdf

app = FastAPI(title="Personalized PDF Service")

# Create DB tables
Base.metadata.create_all(bind=engine)

# Serve generated PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- Schemas ----------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthRequest(BaseModel):
    user_id: str = Field(..., example="user-123")

class GenerateRequest(BaseModel):
    template_name: str = Field(..., example="contract")
    user_profile: Dict[str, str] = Field(..., example={"name": "Alice", "jurisdiction": "CA"})
    extra_prompt: Optional[str] = Field(None, example="Add a confidentiality clause for California law.")

class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None

# ---------- Auth Endpoints ----------
@app.post("/auth/token", response_model=TokenResponse)
def login(auth: AuthRequest):
    # In a real product you would verify credentials.
    token = create_access_token({"sub": auth.user_id})
    return TokenResponse(access_token=token)

# ---------- PDF Generation ----------
@app.post("/pdf/generate", response_model=JobStatusResponse)
def request_pdf(req: GenerateRequest, user=Depends(get_current_user)):
    # Persist job record
    from .database import SessionLocal
    db = SessionLocal()
    job = PdfJob(user_id=user["user_id"], template_name=req.template_name)
    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()
    # Enqueue background task
    generate_pdf.delay(job.id, req.user_profile, req.template_name, req.extra_prompt)
    return JobStatusResponse(job_id=job.id, status=job.status)

@app.get("/pdf/status/{job_id}", response_model=JobStatusResponse)
def get_status(job_id: int, user=Depends(get_current_user)):
    from .database import SessionLocal
    db = SessionLocal()
    job = db.query(PdfJob).filter(PdfJob.id == job_id, PdfJob.user_id == user["user_id"]).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        pdf_url=job.pdf_url,
        error_message=job.error_message,
    )

from celery import Celery
from .config import settings
from .database import SessionLocal
from .models import PdfJob
from .llm_client import generate_text
from .pdf_renderer import render_html, html_to_pdf, save_pdf

celery = Celery(__name__, broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery.task(bind=True, name="generate_pdf")
def generate_pdf(self, job_id: int, user_profile: dict, template_name: str, extra_prompt: str = None):
    db = SessionLocal()
    job = db.query(PdfJob).filter(PdfJob.id == job_id).first()
    if not job:
        return
    try:
        job.status = "processing"
        db.commit()
        # 1️⃣ Build context – static data + LLM‑generated fields
        context = {k: v for k, v in user_profile.items()}
        if extra_prompt:
            generated = generate_text(extra_prompt)
            context["generated_section"] = generated
        # 2️⃣ Render HTML
        html = render_html(template_name, context)
        # 3️⃣ Convert to PDF
        pdf_bytes = html_to_pdf(html)
        # 4️⃣ Store PDF and update job
        pdf_url = save_pdf(pdf_bytes, job_id)
        job.status = "success"
        job.pdf_url = pdf_url
        db.commit()
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        db.commit()
        raise exc
    finally:
        db.close()

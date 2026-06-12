from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .config import settings
from .models import Base, EmailRecord
from .summarizer import EmailSummarizer

engine = create_engine(settings.POSTGRES_DSN)
SessionLocal = sessionmaker(bind=engine)

celery = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

@celery.task(name="process_email")
def process_email_task(message_id: str, sender: str, subject: str, body: str):
    summarizer = EmailSummarizer()
    # Run synchronous wrappers for async calls
    import asyncio
    loop = asyncio.get_event_loop()
    summary = loop.run_until_complete(summarizer.summarize(subject, body))
    priority = loop.run_until_complete(summarizer.priority_score(subject, body))

    db = SessionLocal()
    record = EmailRecord(
        message_id=message_id,
        sender=sender,
        subject=subject,
        summary=summary,
        priority=priority
    )
    db.add(record)
    db.commit()
    db.close()
    return {
        "message_id": message_id,
        "summary": summary,
        "priority": priority
    }

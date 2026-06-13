import os
import subprocess
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .config import settings

# Jinja environment loads templates from ./templates
jinja_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=False,
)

def render_html(template_name: str, context: dict) -> str:
    template = jinja_env.get_template(f"{template_name}.html")
    return template.render(**context)

def html_to_pdf(html: str) -> bytes:
    """Convert HTML string to PDF using WeasyPrint (installed as a Python package).
    Returns the raw PDF bytes.
    """
    from weasyprint import HTML
    return HTML(string=html).write_pdf()

def save_pdf(pdf_bytes: bytes, job_id: int) -> str:
    """Persist PDF to a local folder (could be swapped for S3).
    Returns a public URL path.
    """
    output_dir = Path(__file__).parent.parent / "static" / "pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"job_{job_id}_{uuid.uuid4().hex[:8]}.pdf"
    path = output_dir / filename
    path.write_bytes(pdf_bytes)
    # In production you would return an S3 presigned URL.
    return f"/static/pdfs/{filename}"

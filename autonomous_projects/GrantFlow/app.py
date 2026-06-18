#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, g
from werkzeug.exceptions import HTTPException
from fpdf import FPDF
from models import db, DraftProposal
from utils import generate_proposal_section

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///grantflow.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Helper: get next SBIR deadline (hardcoded to 30 days from now)
def next_deadline():
    return datetime.utcnow() + timedelta(days=30)

# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    logger.exception("Unhandled exception")
    return render_template("error.html", error=str(e)), 500

# Route: Main form
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Route: Draft creation
@app.route("/draft", methods=["POST"])
def draft():
    try:
        # Extract form data
        business = request.form.get("business", "").strip()
        summary = request.form.get("summary", "").strip()
        eligibility = request.form.get("eligibility", "").strip()

        # Validation
        if not business or not summary or not eligibility:
            flash("All fields are required.", "error")
            return redirect(url_for("index"))

        # Generate proposal sections
        proposal_text = generate_proposal_section(business, summary, eligibility)

        # Store draft
        draft = DraftProposal(
            business=business,
            summary=summary,
            eligibility=eligibility,
            proposal_text=proposal_text,
            created_at=datetime.utcnow()
        )
        db.session.add(draft)
        db.session.commit()

        return render_template("preview.html", draft=draft)
    except Exception as exc:
        logger.exception("Error creating draft")
        flash("Failed to create draft. Please try again.", "error")
        return redirect(url_for("index"))

# Route: Download PDF
@app.route("/download/<int:draft_id>", methods=["GET"])
def download(draft_id):
    try:
        draft = DraftProposal.query.get_or_404(draft_id)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Business: {draft.business}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Summary: {draft.summary}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Eligibility: {draft.eligibility}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "Proposal:")
        pdf.ln(5)
        pdf.multi_cell(0, 10, draft.proposal_text)
        pdf_output = f"proposal_{draft_id}.pdf"
        pdf.output(pdf_output)
        return send_file(pdf_output, as_attachment=True, download_name=pdf_output)
    except Exception as exc:
        logger.exception("Error generating PDF")
        flash("Could not generate PDF.", "error")
        return redirect(url_for("index"))

# Route: Status page
@app.route("/status", methods=["GET"])
def status():
    drafts = DraftProposal.query.order_by(DraftProposal.created_at.desc()).all()
    deadline = next_deadline()
    return render_template(
        "status.html",
        drafts=drafts,
        deadline=deadline,
        now=datetime.utcnow()
    )

# CLI command to init database
@app.cli.command("initdb")
def initdb_command():
    """Initialize the database."""
    try:
        db.create_all()
        logger.info("Database initialized.")
        print("Database initialized.")
    except Exception as exc:
        logger.exception("Failed to initialize database")
        print(f"Error: {exc}")

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "initdb":
        with app.app_context():
            initdb_command()
    else:
        app.run(debug=True)
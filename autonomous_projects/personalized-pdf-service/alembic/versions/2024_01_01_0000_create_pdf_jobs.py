"""create pdf_jobs table

Revision ID: 202401010000
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "202401010000"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "pdf_jobs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("template_name", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False, server_default="queued"),
        sa.Column("pdf_url", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.text("now()")),
        sa.Column("error_message", sa.Text, nullable=True),
    )

def downgrade():
    op.drop_table("pdf_jobs")

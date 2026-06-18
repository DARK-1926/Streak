import os
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Base declarative class
Base = declarative_base()

# Database URL pointing to a local SQLite file
DATABASE_URL = "sqlite:///grantflow.db"

# Engine and session factory
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class DraftProposal(Base):
    """
    SQLAlchemy ORM model representing a draft proposal for a small business.
    """

    __tablename__ = "draft_proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_name = Column(String(255), nullable=False)
    project_title = Column(String(255), nullable=False)
    eligibility_score = Column(Integer, nullable=False)
    proposal_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<DraftProposal(id={self.id}, business_name='{self.business_name}', "
            f"project_title='{self.project_title}', eligibility_score={self.eligibility_score}, "
            f"created_at={self.created_at.isoformat()})>"
        )


def db_init() -> None:
    """
    Create the SQLite database file and tables if they do not exist.
    """
    if not os.path.exists("grantflow.db"):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath("grantflow.db")), exist_ok=True)
    # Create all tables defined by Base subclasses
    Base.metadata.create_all(bind=engine)


def create_draft(
    business_name: str,
    project_title: str,
    eligibility_score: int,
    proposal_text: str,
) -> DraftProposal:
    """
    Insert a new DraftProposal record into the database.

    Args:
        business_name: Name of the small business.
        project_title: Title of the proposed project.
        eligibility_score: Integer score representing eligibility.
        proposal_text: Full text of the proposal.

    Returns:
        The created DraftProposal instance.

    Raises:
        ValueError: If any required field is missing or invalid.
        SQLAlchemyError: If the database operation fails.
    """
    if not all([business_name, project_title, proposal_text]):
        raise ValueError("All fields except eligibility_score must be provided.")

    if not isinstance(eligibility_score, int) or eligibility_score < 0:
        raise ValueError("eligibility_score must be a non-negative integer.")

    new_draft = DraftProposal(
        business_name=business_name,
        project_title=project_title,
        eligibility_score=eligibility_score,
        proposal_text=proposal_text,
    )

    try:
        with SessionLocal() as session:
            session.add(new_draft)
            session.commit()
            session.refresh(new_draft)
    except SQLAlchemyError as exc:
        # Rollback on error and re-raise
        session.rollback()
        raise exc

    return new_draft


def get_all_drafts() -> list[DraftProposal]:
    """
    Retrieve all DraftProposal records sorted by creation date (newest first).

    Returns:
        List of DraftProposal instances ordered by created_at descending.
    """
    with SessionLocal() as session:
        drafts = (
            session.query(DraftProposal)
            .order_by(DraftProposal.created_at.desc())
            .all()
        )
    return drafts


# Ensure the database is initialized when this module is imported
db_init()
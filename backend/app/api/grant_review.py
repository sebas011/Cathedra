from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.grant_review_schemas import (
    GrantReviewRead,
    GrantStandardizationUpdate,
    ReviewState,
)
from app.models import FsdpParticipation, Program, Scholar

router = APIRouter(prefix="/fsdp/grant-reviews", tags=["Grant Review"])
LEGACY_SOURCE = "Imported from ScholarDesk"


def legacy_review_statement():
    return (
        select(FsdpParticipation, Scholar, Program)
        .join(Scholar, FsdpParticipation.scholar_id == Scholar.id)
        .join(Program, FsdpParticipation.program_id == Program.id)
        .where(
            Scholar.data_source == LEGACY_SOURCE,
            FsdpParticipation.legacy_grant_label.is_not(None),
            FsdpParticipation.legacy_grant_label != "",
        )
    )


def read_review(
    participation: FsdpParticipation,
    scholar: Scholar,
    program: Program,
) -> GrantReviewRead:
    return GrantReviewRead(
        participation_id=participation.id,
        scholar_id=scholar.id,
        scholar_name=scholar.name,
        department=scholar.department,
        program_name=program.name,
        current_grant_type=participation.grant_type,
        original_grant_label=participation.legacy_grant_label or "",
        standardized_at=participation.grant_standardized_at,
        standardization_note=participation.grant_standardization_note,
    )


@router.get("", response_model=list[GrantReviewRead])
def list_grant_reviews(
    review_state: ReviewState = Query(default="pending", alias="state"),
    db: Session = Depends(get_db),
) -> list[GrantReviewRead]:
    statement = legacy_review_statement()
    if review_state == "pending":
        statement = statement.where(FsdpParticipation.grant_standardized_at.is_(None))
    records = db.execute(
        statement.order_by(Scholar.name, Program.name, FsdpParticipation.id)
    ).all()
    return [read_review(participation, scholar, program) for participation, scholar, program in records]


@router.put("/{participation_id}", response_model=GrantReviewRead)
def standardize_grant(
    participation_id: int,
    payload: GrantStandardizationUpdate,
    db: Session = Depends(get_db),
) -> GrantReviewRead:
    record = db.execute(
        legacy_review_statement().where(FsdpParticipation.id == participation_id)
    ).one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Legacy grant review record not found.")

    participation, scholar, program = record
    original_label = participation.legacy_grant_label
    if not original_label:
        raise HTTPException(status_code=409, detail="The original grant label is unavailable.")

    participation.grant_type = payload.grant_type
    participation.grant_other = original_label
    participation.grant_standardization_note = (payload.note or "").strip() or None
    participation.grant_standardized_at = datetime.now()
    db.commit()
    db.refresh(participation)
    return read_review(participation, scholar, program)

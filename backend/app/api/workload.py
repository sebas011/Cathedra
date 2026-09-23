from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.auth import require_admin
from app.models import FacultyProfile, FacultyWorkload, LocalUser, TeachingAssignment
from app.workload_schemas import (
    FacultyWorkloadCreate,
    FacultyWorkloadRead,
    FacultyWorkloadUpdate,
    TeachingAssignmentRead,
)

router = APIRouter(prefix="/workloads", tags=["Faculty Workload"])


def workload_options():
    return [selectinload(FacultyWorkload.assignments)]


def read_workload(workload: FacultyWorkload, faculty: FacultyProfile) -> FacultyWorkloadRead:
    assignments = [TeachingAssignmentRead.model_validate(item) for item in workload.assignments]
    total_lecture_hours = sum(item.lecture_hours for item in assignments)
    total_laboratory_hours = sum(item.laboratory_hours for item in assignments)
    return FacultyWorkloadRead(
        id=workload.id,
        data_source=workload.data_source,
        faculty_profile_id=faculty.id,
        faculty_name=faculty.name,
        department=faculty.department,
        rank=faculty.rank,
        academic_year=workload.academic_year,
        term=workload.term,
        remarks=workload.remarks,
        assignments=assignments,
        total_lecture_hours=total_lecture_hours,
        total_laboratory_hours=total_laboratory_hours,
        total_weekly_hours=total_lecture_hours + total_laboratory_hours,
        created_at=workload.created_at,
    )


def get_faculty(db: Session, faculty_profile_id: int) -> FacultyProfile:
    faculty = db.get(FacultyProfile, faculty_profile_id)
    if faculty is None:
        raise HTTPException(status_code=404, detail="Faculty member not found.")
    return faculty


def apply_payload(workload: FacultyWorkload, payload: FacultyWorkloadCreate | FacultyWorkloadUpdate) -> None:
    workload.faculty_profile_id = payload.faculty_profile_id
    workload.academic_year = payload.academic_year.strip()
    workload.term = payload.term.strip()
    workload.remarks = payload.remarks.strip() if payload.remarks else None
    workload.assignments.clear()
    workload.assignments.extend(
        TeachingAssignment(
            course_code=assignment.course_code.strip(),
            course_title=assignment.course_title.strip(),
            year_section=assignment.year_section.strip(),
            lecture_hours=assignment.lecture_hours,
            laboratory_hours=assignment.laboratory_hours,
        )
        for assignment in payload.assignments
    )


@router.get("", response_model=list[FacultyWorkloadRead])
def list_workloads(
    search: str = Query(default="", max_length=200),
    academic_year: str = Query(default="", max_length=20),
    term: str = Query(default="", max_length=40),
    db: Session = Depends(get_db),
) -> list[FacultyWorkloadRead]:
    statement = select(FacultyWorkload, FacultyProfile).join(FacultyProfile).options(*workload_options())
    if search.strip():
        search_term = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                FacultyProfile.name.ilike(search_term),
                FacultyProfile.department.ilike(search_term),
                FacultyProfile.rank.ilike(search_term),
                FacultyWorkload.academic_year.ilike(search_term),
                FacultyWorkload.term.ilike(search_term),
            )
        )
    if academic_year.strip():
        statement = statement.where(FacultyWorkload.academic_year == academic_year.strip())
    if term.strip():
        statement = statement.where(FacultyWorkload.term == term.strip())
    records = db.execute(statement.order_by(FacultyProfile.name, FacultyWorkload.academic_year.desc())).unique().all()
    return [read_workload(workload, scholar) for workload, scholar in records]


@router.get("/page")
def paged_workloads(search: str = Query(default="", max_length=200), academic_year: str = Query(default="", max_length=20), term: str = Query(default="", max_length=40), page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=10, le=100), db: Session = Depends(get_db)) -> dict[str, object]:
    statement = select(FacultyWorkload, FacultyProfile).join(FacultyProfile).options(*workload_options())
    if search.strip():
        search_term = f"%{search.strip()}%"
        statement = statement.where(or_(FacultyProfile.name.ilike(search_term), FacultyProfile.department.ilike(search_term), FacultyProfile.rank.ilike(search_term), FacultyWorkload.academic_year.ilike(search_term), FacultyWorkload.term.ilike(search_term)))
    if academic_year.strip(): statement = statement.where(FacultyWorkload.academic_year == academic_year.strip())
    if term.strip(): statement = statement.where(FacultyWorkload.term == term.strip())
    total = db.scalar(select(__import__('sqlalchemy').func.count()).select_from(statement.with_only_columns(FacultyWorkload.id).order_by(None).subquery())) or 0
    records = db.execute(statement.order_by(FacultyProfile.name, FacultyWorkload.academic_year.desc()).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {"items": [read_workload(workload, faculty) for workload, faculty in records], "total": total, "page": page, "page_size": page_size}


@router.get("/summary")
def workload_summary(db: Session = Depends(get_db)) -> dict[str, float | int]:
    totals = db.execute(select(func.count(func.distinct(FacultyWorkload.id)), func.count(TeachingAssignment.id), func.coalesce(func.sum(TeachingAssignment.lecture_hours), 0), func.coalesce(func.sum(TeachingAssignment.laboratory_hours), 0)).select_from(FacultyWorkload).outerjoin(TeachingAssignment)).one()
    return {"workloads": totals[0] or 0, "assignments": totals[1] or 0, "lecture_hours": float(totals[2] or 0), "laboratory_hours": float(totals[3] or 0), "weekly_hours": float((totals[2] or 0) + (totals[3] or 0))}


@router.get("/{workload_id}", response_model=FacultyWorkloadRead)
def get_workload(workload_id: int, db: Session = Depends(get_db)) -> FacultyWorkloadRead:
    record = db.execute(
        select(FacultyWorkload, FacultyProfile)
        .join(FacultyProfile)
        .options(*workload_options())
        .where(FacultyWorkload.id == workload_id)
    ).unique().one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Workload record not found.")
    return read_workload(*record)


@router.post("", response_model=FacultyWorkloadRead, status_code=status.HTTP_201_CREATED)
def create_workload(payload: FacultyWorkloadCreate, db: Session = Depends(get_db)) -> FacultyWorkloadRead:
    get_faculty(db, payload.faculty_profile_id)
    if db.scalar(select(FacultyWorkload).where(FacultyWorkload.faculty_profile_id == payload.faculty_profile_id, FacultyWorkload.academic_year == payload.academic_year.strip(), FacultyWorkload.term == payload.term.strip())):
        raise HTTPException(status_code=409, detail="A workload already exists for this faculty member and period.")
    workload = FacultyWorkload()
    apply_payload(workload, payload)
    db.add(workload)
    db.commit()
    return get_workload(workload.id, db)


@router.put("/{workload_id}", response_model=FacultyWorkloadRead)
def update_workload(
    workload_id: int, payload: FacultyWorkloadUpdate, db: Session = Depends(get_db)
) -> FacultyWorkloadRead:
    workload = db.scalar(
        select(FacultyWorkload).options(*workload_options()).where(FacultyWorkload.id == workload_id)
    )
    if workload is None:
        raise HTTPException(status_code=404, detail="Workload record not found.")
    get_faculty(db, payload.faculty_profile_id)
    apply_payload(workload, payload)
    db.commit()
    return get_workload(workload_id, db)


@router.delete("/{workload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workload(workload_id: int, db: Session = Depends(get_db), _: LocalUser = Depends(require_admin)) -> Response:
    workload = db.get(FacultyWorkload, workload_id)
    if workload is None:
        raise HTTPException(status_code=404, detail="Workload record not found.")
    db.delete(workload)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

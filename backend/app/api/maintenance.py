import csv
import sqlite3
from datetime import datetime
from io import StringIO
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.db import DB_PATH, get_db
from app.auth import require_admin
from app.models import FacultyProfile, FacultyWorkload, FsdpParticipation, LocalUser, Scholar

router = APIRouter(prefix="/maintenance", tags=["Backup & Export"])
BACKUP_DIR = DB_PATH.parent / "backups"
BACKUP_RETENTION = 30


def backup_files() -> list[Path]:
    if not BACKUP_DIR.exists():
        return []
    return sorted(
        BACKUP_DIR.glob("cathedra-backup-*.db"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )


def enforce_backup_retention() -> None:
    for expired in backup_files()[BACKUP_RETENTION:]:
        expired.unlink(missing_ok=True)


def make_backup(source: sqlite3.Connection, destination: Path) -> None:
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
    finally:
        target.close()


def csv_download(filename: str, headings: list[str], rows: list[list[object | None]]) -> Response:
    def export_cell(value: object | None) -> object | None:
        if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
            return f"'{value}"
        return value

    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(headings)
    writer.writerows([[export_cell(value) for value in row] for row in rows])
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/status")
def maintenance_status(db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as caught:
        raise HTTPException(status_code=503, detail="Database connection is unavailable.") from caught

    backups = backup_files()
    latest = backups[0] if backups else None
    return {
        "database_status": "healthy",
        "database_file": DB_PATH.name,
        "database_size_bytes": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
        "fsdp_records": db.scalar(select(func.count()).select_from(Scholar)) or 0,
        "faculty_profiles": db.scalar(select(func.count()).select_from(FacultyProfile)) or 0,
        "workload_records": db.scalar(select(func.count()).select_from(FacultyWorkload)) or 0,
        "backup_count": len(backups),
        "latest_backup_at": datetime.fromtimestamp(latest.stat().st_mtime).astimezone().isoformat() if latest else None,
        "backup_retention": BACKUP_RETENTION,
        "backups": [
            {"filename": item.name, "created_at": datetime.fromtimestamp(item.stat().st_mtime).astimezone().isoformat(), "size_bytes": item.stat().st_size}
            for item in backups
        ],
    }


@router.post("/backups", status_code=status.HTTP_201_CREATED)
def create_database_backup(db: Session = Depends(get_db)) -> dict[str, object]:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination = BACKUP_DIR / f"cathedra-backup-{timestamp}.db"

    try:
        make_backup(db.connection().connection.driver_connection, destination)
        enforce_backup_retention()
    except Exception as caught:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to create database backup.") from caught

    return {
        "filename": destination.name,
        "created_at": datetime.now().astimezone().isoformat(),
        "size_bytes": destination.stat().st_size,
    }


class RestoreRequest(BaseModel):
    filename: str


@router.post("/restore")
def restore_database(
    payload: RestoreRequest,
    db: Session = Depends(get_db),
    _: LocalUser = Depends(require_admin),
) -> dict[str, object]:
    selected = (BACKUP_DIR / Path(payload.filename).name).resolve()
    if selected.parent != BACKUP_DIR.resolve() or not selected.is_file() or selected.suffix != ".db":
        raise HTTPException(status_code=404, detail="The selected backup is not available.")
    try:
        with sqlite3.connect(selected) as source:
            if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise HTTPException(status_code=422, detail="The selected backup could not be verified.")
        pre_restore = BACKUP_DIR / f"cathedra-backup-before-restore-{datetime.now():%Y%m%d-%H%M%S-%f}.db"
        target = db.connection().connection.driver_connection
        make_backup(target, pre_restore)
        with sqlite3.connect(selected) as source:
            source.backup(target)
        enforce_backup_retention()
    except HTTPException:
        raise
    except Exception as caught:
        raise HTTPException(status_code=500, detail="Unable to restore the selected backup.") from caught
    return {"restored_from": selected.name, "safety_backup": pre_restore.name}


@router.get("/exports/fsdp.csv")
def export_fsdp(db: Session = Depends(get_db)) -> Response:
    scholars = db.scalars(
        select(Scholar)
        .options(selectinload(Scholar.participations).selectinload(FsdpParticipation.program))
        .order_by(Scholar.name, Scholar.id)
    ).unique().all()
    rows: list[list[object | None]] = []
    for scholar in scholars:
        base = [
            scholar.id, scholar.name, scholar.age, scholar.previous_degree, scholar.missing_requirements,
            scholar.department, scholar.rank, scholar.tenure, scholar.data_source, scholar.created_at,
            scholar.updated_at,
        ]
        if not scholar.participations:
            rows.append(base + [None] * 9)
            continue
        for participation in scholar.participations:
            rows.append(base + [
                participation.program.name, participation.program.delivering_hei, participation.start_term,
                participation.start_academic_year, participation.end_term, participation.end_academic_year,
                participation.start_date, participation.end_date, participation.grant_type, participation.grant_other,
                participation.status, participation.extension, participation.remarks,
            ])
    return csv_download(
        "cathedra-fsdp.csv",
        ["Scholar ID", "Name", "Age", "Previous Degree", "Missing Requirements", "Department", "Rank", "Tenure", "Source", "Created At", "Updated At", "Program", "Delivering HEI", "Start Term", "Start Academic Year", "End Term", "End Academic Year", "Legacy Start Date", "Legacy End Date", "Grant Type", "Grant Other", "Status", "Extension", "Remarks"],
        rows,
    )


@router.get("/exports/faculty-profiles.csv")
def export_faculty_profiles(db: Session = Depends(get_db)) -> Response:
    profiles = db.scalars(select(FacultyProfile).order_by(FacultyProfile.name, FacultyProfile.id)).all()
    rows = [[profile.id, profile.name, profile.rank, profile.employment_status, profile.salary_grade, profile.college, profile.department, profile.data_source, profile.created_at, profile.updated_at] for profile in profiles]
    return csv_download(
        "cathedra-faculty-profiles.csv",
        ["Faculty ID", "Name", "Academic Rank", "Employment Status", "Salary Grade", "College", "Department", "Source", "Created At", "Updated At"],
        rows,
    )


@router.get("/exports/workloads.csv")
def export_workloads(db: Session = Depends(get_db)) -> Response:
    records = db.execute(
        select(FacultyWorkload, FacultyProfile)
        .join(FacultyProfile)
        .options(selectinload(FacultyWorkload.assignments))
        .order_by(FacultyProfile.name, FacultyWorkload.academic_year.desc(), FacultyWorkload.id)
    ).unique().all()
    rows: list[list[object | None]] = []
    for workload, profile in records:
        base = [workload.id, profile.name, profile.rank, profile.college, profile.department, workload.academic_year, workload.term, workload.remarks, workload.data_source, workload.created_at]
        for assignment in workload.assignments:
            rows.append(base + [assignment.course_code, assignment.course_title, assignment.year_section, assignment.lecture_hours, assignment.laboratory_hours, assignment.lecture_hours + assignment.laboratory_hours])
    return csv_download(
        "cathedra-workloads.csv",
        ["Workload ID", "Faculty Name", "Academic Rank", "College", "Department", "Academic Year", "Term", "Remarks", "Source", "Created At", "Course Code", "Course Title", "Year & Section", "Lecture Hours", "Laboratory Hours", "Total Weekly Hours"],
        rows,
    )

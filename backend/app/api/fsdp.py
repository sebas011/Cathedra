from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import FsdpParticipation, Program, Scholar
from app.schemas import FsdpSummary, ParticipationRead, ProgramCreate, ProgramRead, ProgramUpdate, ScholarCreate, ScholarRead, ScholarUpdate

router = APIRouter(prefix="/fsdp", tags=["FSDP"])
FACULTY_RANK_KEYWORDS = ("faculty", "instructor", "professor", "lecturer", "teacher", "dean")


def personnel_type(rank: str | None) -> str:
    rank_value = (rank or "").lower()
    return "Faculty" if any(keyword in rank_value for keyword in FACULTY_RANK_KEYWORDS) else "Staff"


def options():
    return [selectinload(Scholar.participations).selectinload(FsdpParticipation.program)]


def read_scholar(scholar: Scholar) -> ScholarRead:
    return ScholarRead(id=scholar.id, name=scholar.name, age=scholar.age, previous_degree=scholar.previous_degree, missing_requirements=scholar.missing_requirements, department=scholar.department, rank=scholar.rank, personnel_type=personnel_type(scholar.rank), tenure=scholar.tenure, data_source=scholar.data_source, created_at=scholar.created_at, updated_at=scholar.updated_at, participations=[ParticipationRead(id=item.id, program_id=item.program_id, name=item.program.name, delivering_hei=item.program.delivering_hei, description=item.program.description, start_date=item.start_date, end_date=item.end_date, grant_type=item.grant_type, grant_other=item.grant_other, status=item.status, extension=item.extension, remarks=item.remarks) for item in scholar.participations])


def resolve_program(db: Session, program_name: str, delivering_hei: str | None) -> Program:
    normalized_name = program_name.strip()
    program = db.scalar(select(Program).where(func.lower(Program.name) == normalized_name.lower()))
    if program is None:
        program = Program(name=normalized_name, delivering_hei=delivering_hei)
        db.add(program)
        db.flush()
    elif delivering_hei and not program.delivering_hei:
        program.delivering_hei = delivering_hei
    return program


def apply_payload(db: Session, scholar: Scholar, payload: ScholarCreate | ScholarUpdate) -> None:
    for field, value in payload.model_dump(exclude={"participations"}).items():
        setattr(scholar, field, value)
    scholar.participations.clear()
    db.flush()
    for item in payload.participations:
        scholar.participations.append(FsdpParticipation(program=resolve_program(db, item.program_name, item.delivering_hei), start_date=item.start_date, end_date=item.end_date, grant_type=item.grant_type, grant_other=item.grant_other, status=item.status, extension=item.extension, remarks=item.remarks))


@router.get("/programs", response_model=list[ProgramRead])
def list_programs(db: Session = Depends(get_db)) -> list[Program]:
    return list(db.scalars(select(Program).order_by(Program.name)).all())


@router.post("/programs", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program(payload: ProgramCreate, db: Session = Depends(get_db)) -> Program:
    if db.scalar(select(Program).where(Program.name == payload.name.strip())):
        raise HTTPException(status_code=409, detail="A program with this name already exists.")
    program = Program(**payload.model_dump())
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.put("/programs/{program_id}", response_model=ProgramRead)
def update_program(program_id: int, payload: ProgramUpdate, db: Session = Depends(get_db)) -> Program:
    program = db.get(Program, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    for field, value in payload.model_dump().items():
        setattr(program, field, value)
    db.commit()
    db.refresh(program)
    return program


@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(program_id: int, db: Session = Depends(get_db)) -> Response:
    program = db.get(Program, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    if db.scalar(select(func.count()).select_from(FsdpParticipation).where(FsdpParticipation.program_id == program_id)):
        raise HTTPException(status_code=409, detail="A program with participation history cannot be deleted.")
    db.delete(program)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[ScholarRead])
def list_scholars(search: str = Query(default="", max_length=200), status_filter: str = Query(default="", alias="status", max_length=50), db: Session = Depends(get_db)) -> list[ScholarRead]:
    statement = select(Scholar).options(*options()).distinct()
    if search.strip():
        term = f"%{search.strip()}%"
        statement = statement.outerjoin(Scholar.participations).outerjoin(FsdpParticipation.program).where(or_(Scholar.name.ilike(term), Scholar.department.ilike(term), Scholar.rank.ilike(term), Program.name.ilike(term), Program.delivering_hei.ilike(term)))
    if status_filter.strip():
        statement = statement.join(Scholar.participations).where(FsdpParticipation.status == status_filter.strip())
    return [read_scholar(scholar) for scholar in db.scalars(statement.order_by(Scholar.name, Scholar.id)).unique().all()]


@router.get("/summary", response_model=FsdpSummary)
def summary(db: Session = Depends(get_db)) -> FsdpSummary:
    def count(status_value: str) -> int:
        return db.scalar(select(func.count(func.distinct(FsdpParticipation.scholar_id))).where(FsdpParticipation.status == status_value)) or 0
    return FsdpSummary(total=db.scalar(select(func.count()).select_from(Scholar)) or 0, ongoing=count("On Going"), graduated=count("Graduated"), payback=count("Payback"), withdrawn=count("Withdrawn"), missing_requirements=db.scalar(select(func.count()).select_from(Scholar).where(Scholar.missing_requirements.is_(True))) or 0)


@router.get("/{scholar_id}", response_model=ScholarRead)
def get_scholar(scholar_id: int, db: Session = Depends(get_db)) -> ScholarRead:
    scholar = db.scalar(select(Scholar).options(*options()).where(Scholar.id == scholar_id))
    if scholar is None: raise HTTPException(status_code=404, detail="Scholar not found")
    return read_scholar(scholar)


@router.post("", response_model=ScholarRead, status_code=status.HTTP_201_CREATED)
def create_scholar(payload: ScholarCreate, db: Session = Depends(get_db)) -> ScholarRead:
    scholar = Scholar(); db.add(scholar); apply_payload(db, scholar, payload); db.commit()
    return get_scholar(scholar.id, db)


@router.put("/{scholar_id}", response_model=ScholarRead)
def update_scholar(scholar_id: int, payload: ScholarUpdate, db: Session = Depends(get_db)) -> ScholarRead:
    scholar = db.scalar(select(Scholar).options(*options()).where(Scholar.id == scholar_id))
    if scholar is None: raise HTTPException(status_code=404, detail="Scholar not found")
    apply_payload(db, scholar, payload); db.commit()
    return get_scholar(scholar_id, db)


@router.delete("/{scholar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scholar(scholar_id: int, db: Session = Depends(get_db)) -> Response:
    scholar = db.get(Scholar, scholar_id)
    if scholar is None: raise HTTPException(status_code=404, detail="Scholar not found")
    db.delete(scholar); db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

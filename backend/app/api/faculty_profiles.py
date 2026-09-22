from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import require_admin
from app.faculty_schemas import FacultyProfileCreate, FacultyProfileRead, FacultyProfileUpdate
from app.models import FacultyProfile, LocalUser

router = APIRouter(prefix="/faculty-profiles", tags=["Faculty Profile"])


@router.get("", response_model=list[FacultyProfileRead])
def list_profiles(search: str = Query(default="", max_length=200), db: Session = Depends(get_db)) -> list[FacultyProfile]:
    statement = select(FacultyProfile)
    if search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(or_(FacultyProfile.name.ilike(term), FacultyProfile.rank.ilike(term), FacultyProfile.college.ilike(term), FacultyProfile.department.ilike(term)))
    return list(db.scalars(statement.order_by(FacultyProfile.name)).all())


@router.get("/page")
def paged_profiles(search: str = Query(default="", max_length=200), page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=10, le=100), db: Session = Depends(get_db)) -> dict[str, object]:
    statement = select(FacultyProfile)
    if search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(or_(FacultyProfile.name.ilike(term), FacultyProfile.rank.ilike(term), FacultyProfile.college.ilike(term), FacultyProfile.department.ilike(term)))
    total = db.scalar(select(__import__('sqlalchemy').func.count()).select_from(statement.order_by(None).subquery())) or 0
    items = list(db.scalars(statement.order_by(FacultyProfile.name).offset((page - 1) * page_size).limit(page_size)).all())
    return {"items": [FacultyProfileRead.model_validate(item).model_dump(mode="json") for item in items], "total": total, "page": page, "page_size": page_size}


@router.get("/{profile_id}", response_model=FacultyProfileRead)
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> FacultyProfile:
    profile = db.get(FacultyProfile, profile_id)
    if profile is None: raise HTTPException(status_code=404, detail="Faculty profile not found.")
    return profile


@router.post("", response_model=FacultyProfileRead, status_code=status.HTTP_201_CREATED)
def create_profile(payload: FacultyProfileCreate, db: Session = Depends(get_db)) -> FacultyProfile:
    duplicate = db.scalar(select(FacultyProfile).where(FacultyProfile.name.ilike(payload.name.strip()), FacultyProfile.college == payload.college, FacultyProfile.department.ilike(payload.department.strip())))
    if duplicate:
        raise HTTPException(status_code=409, detail="A faculty profile with this name, college, and department already exists.")
    profile = FacultyProfile(**payload.model_dump()); db.add(profile); db.commit(); db.refresh(profile); return profile


@router.put("/{profile_id}", response_model=FacultyProfileRead)
def update_profile(profile_id: int, payload: FacultyProfileUpdate, db: Session = Depends(get_db)) -> FacultyProfile:
    profile = get_profile(profile_id, db)
    duplicate = db.scalar(select(FacultyProfile).where(FacultyProfile.id != profile_id, FacultyProfile.name.ilike(payload.name.strip()), FacultyProfile.college == payload.college, FacultyProfile.department.ilike(payload.department.strip())))
    if duplicate:
        raise HTTPException(status_code=409, detail="A faculty profile with this name, college, and department already exists.")
    for field, value in payload.model_dump().items(): setattr(profile, field, value)
    db.commit(); db.refresh(profile); return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db), _: LocalUser = Depends(require_admin)) -> Response:
    profile = get_profile(profile_id, db); db.delete(profile); db.commit(); return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.faculty_schemas import FacultyProfileCreate, FacultyProfileRead, FacultyProfileUpdate
from app.models import FacultyProfile

router = APIRouter(prefix="/faculty-profiles", tags=["Faculty Profile"])


@router.get("", response_model=list[FacultyProfileRead])
def list_profiles(search: str = Query(default="", max_length=200), db: Session = Depends(get_db)) -> list[FacultyProfile]:
    statement = select(FacultyProfile)
    if search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(or_(FacultyProfile.name.ilike(term), FacultyProfile.rank.ilike(term), FacultyProfile.college.ilike(term), FacultyProfile.department.ilike(term)))
    return list(db.scalars(statement.order_by(FacultyProfile.name)).all())


@router.get("/{profile_id}", response_model=FacultyProfileRead)
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> FacultyProfile:
    profile = db.get(FacultyProfile, profile_id)
    if profile is None: raise HTTPException(status_code=404, detail="Faculty profile not found.")
    return profile


@router.post("", response_model=FacultyProfileRead, status_code=status.HTTP_201_CREATED)
def create_profile(payload: FacultyProfileCreate, db: Session = Depends(get_db)) -> FacultyProfile:
    profile = FacultyProfile(**payload.model_dump()); db.add(profile); db.commit(); db.refresh(profile); return profile


@router.put("/{profile_id}", response_model=FacultyProfileRead)
def update_profile(profile_id: int, payload: FacultyProfileUpdate, db: Session = Depends(get_db)) -> FacultyProfile:
    profile = get_profile(profile_id, db)
    for field, value in payload.model_dump().items(): setattr(profile, field, value)
    db.commit(); db.refresh(profile); return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db)) -> Response:
    profile = get_profile(profile_id, db); db.delete(profile); db.commit(); return Response(status_code=status.HTTP_204_NO_CONTENT)

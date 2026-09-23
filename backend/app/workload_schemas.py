from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeachingAssignmentInput(BaseModel):
    course_code: str = Field(min_length=1, max_length=50)
    course_title: str = Field(min_length=1, max_length=300)
    year_section: str = Field(min_length=1, max_length=120)
    lecture_hours: float = Field(default=0, ge=0, le=80)
    laboratory_hours: float = Field(default=0, ge=0, le=80)

    @model_validator(mode="after")
    def require_weekly_hours(self) -> "TeachingAssignmentInput":
        if self.lecture_hours + self.laboratory_hours <= 0:
            raise ValueError("Enter lecture or laboratory hours for each course.")
        return self


class FacultyWorkloadBase(BaseModel):
    faculty_profile_id: int = Field(gt=0)
    academic_year: str = Field(min_length=1, max_length=20)
    term: str = Field(min_length=1, max_length=40)
    remarks: str | None = None
    assignments: list[TeachingAssignmentInput] = Field(min_length=1)


class FacultyWorkloadCreate(FacultyWorkloadBase):
    pass


class FacultyWorkloadUpdate(FacultyWorkloadBase):
    pass


class TeachingAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_code: str
    course_title: str
    year_section: str
    lecture_hours: float
    laboratory_hours: float


class FacultyWorkloadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data_source: str
    faculty_profile_id: int
    faculty_name: str
    college: str
    department: str | None
    rank: str | None
    academic_year: str
    term: str
    remarks: str | None
    assignments: list[TeachingAssignmentRead]
    total_lecture_hours: float
    total_laboratory_hours: float
    total_weekly_hours: float
    created_at: datetime

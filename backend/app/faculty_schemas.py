from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CollegeCode = Literal["CAS", "COEd", "CBMA", "COE", "COF", "CIT", "CCS", "CCJ"]
EmploymentStatus = Literal["Full-time", "Part-time"]


class FacultyProfileBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    rank: str = Field(min_length=1, max_length=120)
    employment_status: EmploymentStatus
    salary_grade: str | None = Field(default=None, max_length=30)
    monthly_salary: float | None = Field(default=None, ge=0)
    college: CollegeCode
    department: str = Field(min_length=1, max_length=160)


class FacultyProfileCreate(FacultyProfileBase):
    pass


class FacultyProfileUpdate(FacultyProfileBase):
    pass


class FacultyProfileRead(FacultyProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data_source: str
    created_at: datetime
    updated_at: datetime

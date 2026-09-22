from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SalaryGradeRuleInput(BaseModel):
    salary_grade: str = Field(min_length=1, max_length=30)
    monthly_salary: float = Field(ge=0, le=10_000_000)
    standard_weekly_hours: float = Field(gt=0, le=80)
    overload_hourly_rate: float = Field(ge=0, le=100_000)


class SalaryGradeRuleRead(SalaryGradeRuleInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    updated_at: datetime

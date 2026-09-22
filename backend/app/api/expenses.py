from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_admin
from app.db import get_db
from app.expense_schemas import SalaryGradeRuleInput, SalaryGradeRuleRead
from app.models import FacultyProfile, FacultyWorkload, LocalUser, SalaryGradeRule

router = APIRouter(prefix="/expenses", tags=["Expenses Projection"])


@router.get("/rules", response_model=list[SalaryGradeRuleRead])
def list_rules(db: Session = Depends(get_db)) -> list[SalaryGradeRule]:
    return list(db.scalars(select(SalaryGradeRule).order_by(SalaryGradeRule.salary_grade)).all())


@router.put("/rules/{salary_grade}", response_model=SalaryGradeRuleRead)
def save_rule(salary_grade: str, payload: SalaryGradeRuleInput, db: Session = Depends(get_db), _: LocalUser = Depends(require_admin)) -> SalaryGradeRule:
    if salary_grade.strip().lower() != payload.salary_grade.strip().lower():
        raise HTTPException(status_code=400, detail="The salary grade in the address must match the saved rule.")
    rule = db.scalar(select(SalaryGradeRule).where(SalaryGradeRule.salary_grade == payload.salary_grade.strip()))
    if rule is None:
        rule = SalaryGradeRule(**payload.model_dump())
        db.add(rule)
    else:
        for field, value in payload.model_dump().items():
            setattr(rule, field, value)
    db.commit(); db.refresh(rule)
    return rule


@router.get("/projection")
def project_expenses(
    academic_year: str = Query(min_length=1, max_length=20),
    term: str = Query(min_length=1, max_length=40),
    teaching_weeks: float = Query(default=18, gt=0, le=52),
    salary_months: float = Query(default=5, gt=0, le=12),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    rules = {rule.salary_grade.lower(): rule for rule in db.scalars(select(SalaryGradeRule)).all()}
    workloads = db.execute(select(FacultyWorkload, FacultyProfile).join(FacultyProfile).options(selectinload(FacultyWorkload.assignments)).where(FacultyWorkload.academic_year == academic_year.strip(), FacultyWorkload.term == term.strip()).order_by(FacultyProfile.name)).unique().all()
    records = []
    for workload, faculty in workloads:
        weekly_hours = sum(item.lecture_hours + item.laboratory_hours for item in workload.assignments)
        rule = rules.get((faculty.salary_grade or "").lower())
        excess_hours = max(weekly_hours - rule.standard_weekly_hours, 0) if rule else 0
        regular_cost = rule.monthly_salary * salary_months if rule else 0
        overload_cost = excess_hours * rule.overload_hourly_rate * teaching_weeks if rule else 0
        records.append({"faculty_id": faculty.id, "faculty_name": faculty.name, "department": faculty.department, "salary_grade": faculty.salary_grade, "weekly_hours": weekly_hours, "standard_weekly_hours": rule.standard_weekly_hours if rule else None, "overload_hours": excess_hours, "regular_cost": regular_cost, "overload_cost": overload_cost, "projected_cost": regular_cost + overload_cost, "rule_available": rule is not None})
    return {"academic_year": academic_year.strip(), "term": term.strip(), "teaching_weeks": teaching_weeks, "salary_months": salary_months, "records": records, "total_regular_cost": sum(item["regular_cost"] for item in records), "total_overload_cost": sum(item["overload_cost"] for item in records), "total_projected_cost": sum(item["projected_cost"] for item in records), "missing_rules": sum(not item["rule_available"] for item in records)}

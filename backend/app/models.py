from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Scholar(Base):
    __tablename__ = "scholars"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    age: Mapped[int | None] = mapped_column(Integer)
    previous_degree: Mapped[str | None] = mapped_column(String(300))
    missing_requirements: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department: Mapped[str | None] = mapped_column(String(120), index=True)
    rank: Mapped[str | None] = mapped_column(String(120))
    tenure: Mapped[str | None] = mapped_column(String(120))
    data_source: Mapped[str] = mapped_column(String(30), default="Cathedra", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    participations: Mapped[list["FsdpParticipation"]] = relationship(
        back_populates="scholar", cascade="all, delete-orphan"
    )


class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    rank: Mapped[str] = mapped_column(String(120), nullable=False)
    employment_status: Mapped[str] = mapped_column(String(20), nullable=False)
    salary_grade: Mapped[str | None] = mapped_column(String(30))
    college: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    data_source: Mapped[str] = mapped_column(String(30), default="Cathedra", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, unique=True, index=True)
    delivering_hei: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)

    participations: Mapped[list["FsdpParticipation"]] = relationship(back_populates="program")


class FsdpParticipation(Base):
    __tablename__ = "fsdp_participations"
    __table_args__ = (Index("ix_fsdp_participations_status_scholar", "status", "scholar_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scholar_id: Mapped[int] = mapped_column(ForeignKey("scholars.id"), nullable=False, index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False, index=True)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="Active", nullable=False, index=True)
    grant_type: Mapped[str | None] = mapped_column(String(100))
    grant_other: Mapped[str | None] = mapped_column(String(200))
    legacy_grant_label: Mapped[str | None] = mapped_column(String(200))
    grant_standardized_at: Mapped[datetime | None] = mapped_column(DateTime)
    grant_standardization_note: Mapped[str | None] = mapped_column(String(500))
    extension: Mapped[str | None] = mapped_column(String(200))
    remarks: Mapped[str | None] = mapped_column(Text)

    scholar: Mapped[Scholar] = relationship(back_populates="participations")
    program: Mapped[Program] = relationship(back_populates="participations")


class FacultyWorkload(Base):
    __tablename__ = "faculty_workloads"
    __table_args__ = (Index("ix_faculty_workloads_period_faculty", "academic_year", "term", "faculty_profile_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_profile_id: Mapped[int] = mapped_column(ForeignKey("faculty_profiles.id"), nullable=False, index=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    term: Mapped[str] = mapped_column(String(40), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    data_source: Mapped[str] = mapped_column(String(30), default="Cathedra", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    assignments: Mapped[list["TeachingAssignment"]] = relationship(
        back_populates="workload", cascade="all, delete-orphan"
    )


class TeachingAssignment(Base):
    __tablename__ = "teaching_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    workload_id: Mapped[int] = mapped_column(ForeignKey("faculty_workloads.id"), nullable=False, index=True)
    course_code: Mapped[str] = mapped_column(String(50), nullable=False)
    course_title: Mapped[str] = mapped_column(String(300), nullable=False)
    year_section: Mapped[str] = mapped_column(String(120), nullable=False)
    lecture_hours: Mapped[float] = mapped_column(default=0, nullable=False)
    laboratory_hours: Mapped[float] = mapped_column(default=0, nullable=False)
    workload: Mapped[FacultyWorkload] = relationship(back_populates="assignments")


class LocalUser(Base):
    __tablename__ = "local_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="staff")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)


class LocalSession(Base):
    __tablename__ = "local_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("local_users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class SalaryGradeRule(Base):
    __tablename__ = "salary_grade_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    salary_grade: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    monthly_salary: Mapped[float] = mapped_column(nullable=False)
    standard_weekly_hours: Mapped[float] = mapped_column(nullable=False, default=18)
    overload_hourly_rate: Mapped[float] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class ActivityEvent(Base):
    __tablename__ = "activity_events"
    __table_args__ = (Index("ix_activity_events_created_id", "created_at", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(80), nullable=True)
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    area: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False, index=True)

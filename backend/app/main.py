from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text
import os
from pathlib import Path

from app.api.fsdp import router as fsdp_router
from app.api.faculty_profiles import router as faculty_profiles_router
from app.api.grant_review import router as grant_review_router
from app.api.workload import router as workload_router
from app.api.maintenance import router as maintenance_router
from app.api.auth import router as auth_router
from app.api.expenses import router as expenses_router
from app.api.activity import router as activity_router
from app.auth import require_signed_in

EXPENSES_PROJECTION_ENABLED = False
from app.db import Base, engine
from app.db import SessionLocal
from app.models import ActivityEvent

Base.metadata.create_all(bind=engine)

with engine.begin() as connection:
    participation_columns = connection.execute(
        text("PRAGMA table_info(fsdp_participations)")
    ).mappings().all()
    existing = {column["name"] for column in participation_columns}
    if participation_columns and "grant_type" not in existing:
        connection.execute(text("ALTER TABLE fsdp_participations ADD COLUMN grant_type VARCHAR(100)"))
    if participation_columns and "grant_other" not in existing:
        connection.execute(text("ALTER TABLE fsdp_participations ADD COLUMN grant_other VARCHAR(200)"))
    if participation_columns and "legacy_grant_label" not in existing:
        connection.execute(text("ALTER TABLE fsdp_participations ADD COLUMN legacy_grant_label VARCHAR(200)"))
    if participation_columns and "grant_standardized_at" not in existing:
        connection.execute(text("ALTER TABLE fsdp_participations ADD COLUMN grant_standardized_at DATETIME"))
    if participation_columns and "grant_standardization_note" not in existing:
        connection.execute(text("ALTER TABLE fsdp_participations ADD COLUMN grant_standardization_note VARCHAR(500)"))
    for table_name in ("scholars", "faculty_profiles", "faculty_workloads"):
        columns = connection.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()
        if columns and "data_source" not in {column["name"] for column in columns}:
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN data_source VARCHAR(30) NOT NULL DEFAULT 'Cathedra'"))
    connection.execute(
        text(
            "UPDATE fsdp_participations "
            "SET legacy_grant_label = grant_other "
            "WHERE (legacy_grant_label IS NULL OR legacy_grant_label = '') "
            "AND grant_other IS NOT NULL AND trim(grant_other) <> '' "
            "AND EXISTS (SELECT 1 FROM scholars "
            "WHERE scholars.id = fsdp_participations.scholar_id "
            "AND scholars.data_source = 'Imported from ScholarDesk')"
        )
    )
    # These indexes also apply to offices upgrading from an earlier Cathedra
    # release, where create_all() does not modify existing tables.
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_fsdp_participations_status_scholar ON fsdp_participations (status, scholar_id)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_faculty_workloads_period_faculty ON faculty_workloads (academic_year, term, faculty_profile_id)"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_activity_events_created_id ON activity_events (created_at, id)"))
    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_scholars_name ON scholars (name)"))
    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_faculty_profiles_identity ON faculty_profiles (name, college, department)"))
    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_faculty_workloads_period ON faculty_workloads (faculty_profile_id, academic_year, term)"))

app = FastAPI(title="Cathedra R1 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def activity_details(path: str, method: str) -> tuple[str, str] | None:
    if not path.startswith("/api/v1/") or method not in {"POST", "PUT", "DELETE"}:
        return None
    if path.startswith("/api/v1/auth/login") or path.startswith("/api/v1/auth/logout") or path.startswith("/api/v1/auth/setup"):
        return None
    area = path.removeprefix("/api/v1/").split("/", 1)[0]
    labels = {"fsdp": "FSDP", "faculty-profiles": "Faculty Profiles", "workloads": "Faculty Workload", "maintenance": "Backup & Export", "auth": "Local Accounts", "expenses": "Expenses Projection"}
    verbs = {"POST": "Created or started", "PUT": "Updated", "DELETE": "Deleted"}
    return labels.get(area, area.replace("-", " ").title()), f"{verbs[method]} {labels.get(area, area.replace('-', ' ').title())}"


@app.middleware("http")
async def record_activity(request, call_next):
    response = await call_next(request)
    detail = activity_details(request.url.path, request.method)
    user = getattr(request.state, "local_user", None)
    if detail and user is not None and response.status_code < 400:
        db = SessionLocal()
        try:
            db.add(ActivityEvent(user_id=user.id, username=user.username, area=detail[0], action=detail[1]))
            db.commit()
        finally:
            db.close()
    return response


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(grant_review_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(auth_router, prefix="/api/v1")
app.include_router(fsdp_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(faculty_profiles_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(workload_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(maintenance_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
if EXPENSES_PROJECTION_ENABLED:
    app.include_router(expenses_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(activity_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])

_default_frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_DIST = Path(os.environ.get("CATHEDRA_FRONTEND_DIST", _default_frontend_dist)).resolve()
FRONTEND_INDEX = FRONTEND_DIST / "index.html"


@app.get("/{path:path}", include_in_schema=False)
def serve_frontend(path: str) -> FileResponse:
    if path == "api" or path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found.")
    if not FRONTEND_INDEX.exists():
        raise HTTPException(status_code=404, detail="Frontend assets have not been built.")
    requested_file = (FRONTEND_DIST / path).resolve()
    if FRONTEND_DIST in requested_file.parents and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(FRONTEND_INDEX)

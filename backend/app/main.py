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
from app.auth import require_signed_in
from app.db import Base, engine

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

app = FastAPI(title="Cathedra R1 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(grant_review_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(auth_router, prefix="/api/v1")
app.include_router(fsdp_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(faculty_profiles_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(workload_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])
app.include_router(maintenance_router, prefix="/api/v1", dependencies=[Depends(require_signed_in)])

_default_frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_DIST = Path(os.environ.get("CATHEDRA_FRONTEND_DIST", _default_frontend_dist)).resolve()
FRONTEND_INDEX = FRONTEND_DIST / "index.html"


@app.get("/{path:path}", include_in_schema=False)
def serve_frontend(path: str) -> FileResponse:
    if not FRONTEND_INDEX.exists():
        raise HTTPException(status_code=404, detail="Frontend assets have not been built.")
    requested_file = (FRONTEND_DIST / path).resolve()
    if FRONTEND_DIST in requested_file.parents and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(FRONTEND_INDEX)

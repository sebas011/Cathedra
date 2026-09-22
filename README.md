# Cathedra R1 — Foundation + FSDP

Incremental rebuild of Cathedra. This package intentionally implements only:

- Shared application shell
- Local account setup and sign-in
- Dashboard for the three major Cathedra modules
- Sidebar/top navigation
- FSDP list/search/filter view
- Scholar detail view and repeatable assignment/program participation editors
- Normalized FSDP CRUD API with reusable programs and assignments

The Faculty Workload and Expenses Projection modules are placeholders for later phases.

## Stack

- FastAPI + SQLAlchemy
- SQLite for the first local development milestone (PostgreSQL-ready SQLAlchemy models)
- React + TypeScript + Vite
- Plain CSS design system inspired by the provided administrator screenshots

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8100
```

API docs: http://127.0.0.1:8100/docs

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173

## Local accounts

On the first visit, create the local administrator account with a password of at least 10 characters. The administrator can add staff accounts from **Backup & Export**. Sessions expire after 12 hours. Cathedra remains local-only; it is not intended to be exposed on a network.

## Tests

```powershell
cd backend
pytest -q
```

```powershell
cd frontend
npm run build
```

## Production boundary

This project does not read or modify the current Phase 21.6 production installation or `C:\ScholarDesk\grants.db`.

# Cathedra Office Deployment Guide

## Purpose

For a standard office installation, use the self-contained desktop release described in [DESKTOP_RELEASE.md](DESKTOP_RELEASE.md). The manual Python and Node.js steps below remain available for developer testing and local troubleshooting. Cathedra is separate from the previous ScholarDesk installation.

> Do not extract this package into `C:\ScholarDesk`, and do not replace or edit `C:\ScholarDesk\grants.db`.

## Package contents

The deployment backup contains the Cathedra source code, setup files, and the active local database:

- `backend\scholardesk_v2_dev.db` — active Cathedra data
- `backend\app` — API and database logic
- `frontend\src` — application interface
- `backend\requirements.txt` and `frontend\package.json` — install requirements

The package intentionally excludes installed dependencies and generated build files. Install them on the office computer using the steps below.

## Before you start

- Use a Windows office computer with Python and Node.js installed.
- Extract the deployment ZIP to a new folder such as `C:\Cathedra`.
- Keep the extracted folder in a location backed up by the office’s normal file backup process.
- Start only the local services shown below; they bind to `127.0.0.1`, so they are available only on that computer.

## First-time setup

Open PowerShell in the extracted Cathedra folder.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Open a second PowerShell window in the same extracted Cathedra folder.

```powershell
cd frontend
npm install
```

## Start Cathedra

In the first PowerShell window:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8100
```

In the second PowerShell window:

```powershell
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173` in a browser. On the first visit, create the local administrator account using a password of at least 10 characters. The administrator can add staff accounts in **Backup & Export**. Do not expose this setup to a network.

## Everyday backup and export

Before making major changes or at the end of the workday:

1. Open **Backup & Export** in Cathedra’s sidebar.
2. Confirm the database status is **Healthy**.
3. Select **Create Backup**. Cathedra writes a timestamped snapshot to `backend\backups` and keeps the newest 30 backups.
4. Download the needed CSV export for FSDP, faculty profiles, or workloads.

The original source text for imported grants is retained in Cathedra. Use **Grant Review** to standardize a label while maintaining its legacy value and decision timestamp.

## Restore a Cathedra backup

An administrator can restore a backup directly in **Backup & Export**. Select the desired snapshot and choose **Restore Selected Backup**. Cathedra verifies the backup and creates a safety copy before it restores anything. Sign in again if prompted afterward.

Never use this procedure on `C:\ScholarDesk\grants.db`.

## Quick acceptance check

After installation, verify that:

- The dashboard opens at `http://127.0.0.1:5173`.
- **Backup & Export** shows a healthy database and non-zero imported FSDP data when expected.
- **Grant Review** lists preserved legacy labels when pending reviews exist.
- The API reference opens at `http://127.0.0.1:8100/docs`.

For a technical issue, retain the deployment ZIP and the latest `backend\backups` snapshot before making changes.

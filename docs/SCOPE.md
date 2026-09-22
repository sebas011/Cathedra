# Rebuild scope

ScholarDesk v2 is being rebuilt module-by-module instead of recreating the whole application at once.

## Three principal modules

1. Faculty and Staff Development Program (FSDP)
2. Faculty Workload
3. Expenses Projection

## Current milestone

The current milestone establishes the common application shell and implements FSDP first.

### Included

- Login screen (development shell only)
- Dashboard
- Persistent sidebar and top header
- Responsive mobile navigation
- Reusable card, badge, button, input, and table styling
- FSDP directory
- Search and status/type filters
- FSDP record creation
- FSDP record editing
- FSDP record deletion with confirmation
- FastAPI CRUD endpoints
- Local SQLite development persistence

### Deferred

- Production authentication and role-based authorization
- Data migration from Phase 21.6
- Faculty Workload implementation
- Expenses Projection implementation
- Audit persistence
- Backup/restore
- Operational diagnostics

The existing Phase 21.6 system remains the production reference until v2 reaches migration parity and release acceptance.

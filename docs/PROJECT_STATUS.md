# Cathedra Project Status

## Frozen checkpoint — 2026-09-22

Active development is paused at the GitHub checkpoint following the local accounts, safe backup and restore, and salary-grade Expenses Projection work.

## Expenses Projection

The Expenses Projection source code and test remain in the project, but the module is intentionally disabled:

- It is hidden from the sidebar and marked **Paused** on the dashboard.
- The `/api/v1/expenses` API is not registered while `EXPENSES_PROJECTION_ENABLED` is `False` in `backend/app/main.py`.

To resume it, set that flag to `True`, restore the `ExpensesPage` route and navigation item, then run the backend tests and frontend production build before publishing a new checkpoint.

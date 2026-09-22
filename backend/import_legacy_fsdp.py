import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


OLD_DATABASE = Path(r"C:\Users\rodia\Desktop\ScholarDesk\grants.db")
TARGET_DATABASE = Path(__file__).parent / "scholardesk_v2_dev.db"
STATUS_MAP = {"Ongoing": "On Going", "Graduated": "Graduated", "Discontinued": "Withdrawn"}


def main() -> None:
    backup = TARGET_DATABASE.with_name(
        f"scholardesk_v2_dev.pre-fsdp-import-{datetime.now():%Y%m%d-%H%M%S}.db"
    )
    shutil.copy2(TARGET_DATABASE, backup)
    source = sqlite3.connect(f"file:{OLD_DATABASE.as_posix()}?mode=ro", uri=True)
    target = sqlite3.connect(TARGET_DATABASE)
    target.execute("PRAGMA foreign_keys = ON")
    source.row_factory = sqlite3.Row
    departments = {
        row["scholar_id"]: row
        for row in source.execute(
            """SELECT department, rank, tenure, scholar_id FROM department_assignments
               WHERE date_ended IS NULL OR date_ended = '' ORDER BY id"""
        )
    }
    imported_scholars = imported_grants = 0
    try:
        for scholar in source.execute("SELECT * FROM scholars ORDER BY id"):
            assignment = departments.get(scholar["id"])
            cursor = target.execute(
                """INSERT INTO scholars (name, age, previous_degree, missing_requirements, department, rank, tenure, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (scholar["name"], scholar["age"], scholar["previous_degree"], scholar["missing_requirements"], assignment["department"] if assignment else None, assignment["rank"] if assignment else None, assignment["tenure"] if assignment else None),
            )
            imported_scholars += 1
            for grant in source.execute("SELECT * FROM grants WHERE scholar_id = ? ORDER BY id", (scholar["id"],)):
                program_name = (grant["program_applied"] or "Unspecified Program").strip()
                program = target.execute("SELECT id FROM programs WHERE lower(name) = lower(?)", (program_name,)).fetchone()
                if program is None:
                    program_id = target.execute("INSERT INTO programs (name, delivering_hei) VALUES (?, ?)", (program_name, grant["delivering_hei"])).lastrowid
                else:
                    program_id = program[0]
                target.execute(
                    """INSERT INTO fsdp_participations (scholar_id, program_id, start_date, end_date, status, grant_type, extension, remarks)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cursor.lastrowid, program_id, grant["date_started"], grant["date_ended"], STATUS_MAP.get(grant["status"], "On Going"), grant["type_of_grant"], grant["extension"], grant["remarks"]),
                )
                imported_grants += 1
        target.commit()
    except Exception:
        target.rollback()
        raise
    finally:
        source.close()
        target.close()
    print(f"Imported {imported_scholars} scholars and {imported_grants} grants. Backup: {backup}")


if __name__ == "__main__":
    main()

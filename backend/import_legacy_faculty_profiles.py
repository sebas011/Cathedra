import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


SOURCE = Path(r"C:\Users\rodia\Desktop\ScholarDesk\grants.db")
TARGET = Path(__file__).parent / "scholardesk_v2_dev.db"


def full_name(row: sqlite3.Row) -> str:
    return " ".join(part for part in (row["first_name"], row["middle_name"], row["last_name"], row["suffix"]) if part).strip()


def main() -> None:
    backup = TARGET.with_name(f"scholardesk_v2_dev.pre-faculty-import-{datetime.now():%Y%m%d-%H%M%S}.db")
    shutil.copy2(TARGET, backup)
    source = sqlite3.connect(f"file:{SOURCE.as_posix()}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    target = sqlite3.connect(TARGET)
    try:
        for faculty in source.execute("SELECT * FROM faculty ORDER BY id"):
            college = source.execute("SELECT code FROM faculty_colleges WHERE id = ?", (faculty["home_college_id"],)).fetchone()
            rank = source.execute("SELECT name, salary_grade FROM academic_ranks WHERE id = ?", (faculty["current_rank_id"],)).fetchone()
            program = source.execute("SELECT name FROM faculty_programs WHERE id = ?", (faculty["home_program_id"],)).fetchone()
            target.execute(
                """INSERT INTO faculty_profiles (id, name, rank, employment_status, salary_grade, college, department, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (faculty["id"], full_name(faculty), rank[0] if rank else "Not specified", "Full-time" if faculty["is_active"] else "Part-time", rank[1] if rank else None, college[0] if college else "CAS", program[0] if program else "Not specified"),
            )
        target.commit()
    except Exception:
        target.rollback()
        raise
    finally:
        source.close(); target.close()
    print(f"Imported 347 faculty profiles. Backup: {backup}")


if __name__ == "__main__":
    main()

from app.db import get_db
from app.main import app
from app.models import FsdpParticipation, Scholar


def legacy_grant_payload() -> dict[str, object]:
    return {
        "name": "Legacy Grant Scholar",
        "age": 40,
        "previous_degree": "Master of Arts",
        "missing_requirements": False,
        "department": "College of Arts and Sciences",
        "rank": "Instructor I",
        "tenure": "Permanent",
        "participations": [
            {
                "program_name": "Doctor of Education",
                "delivering_hei": "Example University",
                "grant_type": "Others",
                "grant_other": "Partial FSDP",
                "status": "On Going",
            }
        ],
    }


def test_standardization_preserves_legacy_grant_label(client) -> None:
    created = client.post("/api/v1/fsdp", json=legacy_grant_payload())
    assert created.status_code == 201
    scholar_id = created.json()["id"]
    participation_id = created.json()["participations"][0]["id"]

    session_generator = app.dependency_overrides[get_db]()
    db = next(session_generator)
    try:
        scholar = db.get(Scholar, scholar_id)
        participation = db.get(FsdpParticipation, participation_id)
        assert scholar is not None
        assert participation is not None
        scholar.data_source = "Imported from ScholarDesk"
        participation.legacy_grant_label = "Partial FSDP"
        db.commit()
    finally:
        session_generator.close()

    pending = client.get("/api/v1/fsdp/grant-reviews?state=pending")
    assert pending.status_code == 200
    assert pending.json()[0]["original_grant_label"] == "Partial FSDP"

    updated = client.put(
        f"/api/v1/fsdp/grant-reviews/{participation_id}",
        json={"grant_type": "Partial Scholarship", "note": "Legacy FSDP label mapped by admin."},
    )
    assert updated.status_code == 200
    assert updated.json()["current_grant_type"] == "Partial Scholarship"
    assert updated.json()["standardized_at"] is not None

    scholar = client.get(f"/api/v1/fsdp/{scholar_id}")
    grant = scholar.json()["participations"][0]
    assert grant["grant_type"] == "Partial Scholarship"
    assert grant["grant_other"] == "Partial FSDP"

    all_reviews = client.get("/api/v1/fsdp/grant-reviews?state=all")
    assert all_reviews.json()[0]["standardization_note"] == "Legacy FSDP label mapped by admin."

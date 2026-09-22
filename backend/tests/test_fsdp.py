def payload(name: str) -> dict[str, object]:
    return {
        "name": name,
        "age": 34,
        "previous_degree": "Bachelor of Science in Information Technology",
        "missing_requirements": False,
        "department": "College of Information Technology",
        "rank": "Instructor II",
        "tenure": "Permanent",
        "participations": [
            {
                "program_name": "Master of Information Systems",
                "delivering_hei": "Example University",
                "start_date": "2024-06-01",
                "grant_type": "Full Scholarship",
                "status": "On Going",
            }
        ],
    }


def test_reuses_program_for_multiple_scholars(client) -> None:
    maria = client.post("/api/v1/fsdp", json=payload("Maria Santos"))
    assert maria.status_code == 201
    assert maria.json()["personnel_type"] == "Faculty"

    juan = payload("Juan Dela Cruz")
    juan["rank"] = "Administrative Officer"
    assert client.post("/api/v1/fsdp", json=juan).status_code == 201

    programs = client.get("/api/v1/fsdp/programs")
    assert programs.status_code == 200
    assert len(programs.json()) == 1


def test_age_must_be_in_the_allowed_range(client) -> None:
    invalid = payload("Maria Santos")
    invalid["age"] = 17
    assert client.post("/api/v1/fsdp", json=invalid).status_code == 422

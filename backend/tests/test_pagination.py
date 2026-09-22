from test_fsdp import payload


def faculty_payload(name: str) -> dict[str, str]:
    return {"name": name, "rank": "Instructor I", "employment_status": "Full-time", "salary_grade": "SG 12", "college": "CIT", "department": "Information Technology"}


def test_fsdp_page_returns_a_bounded_result_and_total(client) -> None:
    for index in range(11):
        response = client.post("/api/v1/fsdp", json=payload(f"Scholar {index:02d}"))
        assert response.status_code == 201

    first = client.get("/api/v1/fsdp/page?page=1&page_size=10")
    second = client.get("/api/v1/fsdp/page?page=2&page_size=10")
    assert first.status_code == 200 and second.status_code == 200
    assert first.json()["total"] == 11
    assert len(first.json()["items"]) == 10
    assert len(second.json()["items"]) == 1


def test_faculty_and_workload_pages_respect_filters(client) -> None:
    first = client.post("/api/v1/faculty-profiles", json=faculty_payload("Ada Cruz"))
    second = client.post("/api/v1/faculty-profiles", json=faculty_payload("Bela Cruz"))
    assert first.status_code == 201 and second.status_code == 201
    faculty_page = client.get("/api/v1/faculty-profiles/page?search=Ada&page_size=10")
    assert faculty_page.status_code == 200
    assert faculty_page.json()["total"] == 1

    workload = client.post("/api/v1/workloads", json={"faculty_profile_id": first.json()["id"], "academic_year": "2026-2027", "term": "First Semester", "remarks": "", "assignments": [{"course_code": "IT101", "course_title": "Computing", "year_section": "1A", "lecture_hours": 3, "laboratory_hours": 0}]})
    assert workload.status_code == 201
    workload_page = client.get("/api/v1/workloads/page?academic_year=2026-2027&page_size=10")
    assert workload_page.status_code == 200
    assert workload_page.json()["total"] == 1
    assert workload_page.json()["items"][0]["faculty_name"] == "Ada Cruz"

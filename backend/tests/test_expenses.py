def test_salary_grade_projection_uses_workload_and_rule(client) -> None:
    faculty = client.post("/api/v1/faculty-profiles", json={"name":"Ana Reyes","rank":"Instructor I","employment_status":"Full-time","salary_grade":"12","college":"CIT","department":"Computing"})
    assert faculty.status_code == 201
    workload = client.post("/api/v1/workloads", json={"faculty_profile_id":faculty.json()["id"],"academic_year":"2026-2027","term":"First Semester","remarks":"","assignments":[{"course_code":"IT101","course_title":"Systems","year_section":"1A","lecture_hours":20,"laboratory_hours":0}]})
    assert workload.status_code == 201
    rule = client.put("/api/v1/expenses/rules/12", json={"salary_grade":"12","monthly_salary":30000,"standard_weekly_hours":18,"overload_hourly_rate":250})
    assert rule.status_code == 200
    projection = client.get("/api/v1/expenses/projection?academic_year=2026-2027&term=First%20Semester&teaching_weeks=18&salary_months=5")
    assert projection.status_code == 200
    data = projection.json()
    assert data["total_regular_cost"] == 150000
    assert data["total_overload_cost"] == 9000
    assert data["total_projected_cost"] == 159000

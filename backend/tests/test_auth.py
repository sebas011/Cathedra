def test_records_require_a_local_session(client) -> None:
    client.headers.clear()
    response = client.get("/api/v1/fsdp")
    assert response.status_code == 401


def test_administrator_can_create_staff_account(client) -> None:
    response = client.post(
        "/api/v1/auth/users",
        json={"username": "office-staff", "password": "staff-password-123", "role": "staff"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "staff"
    history = client.get("/api/v1/activity")
    assert history.status_code == 200
    assert history.json()[0]["area"] == "Local Accounts"

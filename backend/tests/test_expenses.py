def test_expense_projection_api_is_disabled_while_project_is_frozen(client) -> None:
    response = client.get("/api/v1/expenses/rules")
    assert response.status_code == 404

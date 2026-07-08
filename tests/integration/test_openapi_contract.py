def test_openapi_contains_task_routes(client) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    paths = data.get("paths", {})
    assert "/api/v1/tasks" in paths
    assert "/api/v1/tasks/{task_id}" in paths

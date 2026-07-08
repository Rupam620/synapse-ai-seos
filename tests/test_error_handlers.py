def test_standardized_error_response_for_not_found(client):
    res = client.get("/api/v1/tasks/123456")
    assert res.status_code == 404
    body = res.json()
    assert set(body.keys()) == {"error_code", "message", "details", "request_id"}
    assert body["error_code"] == "NOT_FOUND"

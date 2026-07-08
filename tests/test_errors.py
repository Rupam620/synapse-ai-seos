def test_not_found_error_shape(client):
    r = client.get("/api/v1/tasks/999999")
    assert r.status_code == 404
    body = r.json()
    assert body["error_code"] == "NOT_FOUND"
    assert "message" in body
    assert "request_id" in body

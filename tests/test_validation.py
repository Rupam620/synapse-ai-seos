def test_create_validation_rejects_unknown_field(client):
    payload = {
        "title": "Task",
        "status": "todo",
        "priority": "medium",
        "unknown": "x",
    }
    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "VALIDATION_ERROR"


def test_create_validation_rejects_invalid_enum(client):
    payload = {
        "title": "Task",
        "status": "bad",
        "priority": "medium",
    }
    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 422


def test_put_requires_full_payload(client):
    r = client.post("/api/v1/tasks", json={"title": "Task", "status": "todo", "priority": "medium"})
    task_id = r.json()["id"]

    r = client.put(f"/api/v1/tasks/{task_id}", json={"title": "Only title"})
    assert r.status_code == 422

def test_task_crud_flow(client):
    create_payload = {
        "title": "Initial task",
        "description": "Do thing",
        "status": "todo",
        "priority": 3,
    }
    create_res = client.post("/api/v1/tasks/", json=create_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] > 0
    task_id = created["id"]

    get_res = client.get(f"/api/v1/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Initial task"

    list_res = client.get("/api/v1/tasks/?status=todo&priority=3&limit=10&offset=0")
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert list_body["total"] == 1
    assert len(list_body["items"]) == 1

    patch_res = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "in_progress"

    delete_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_res.status_code == 204

    get_after_delete = client.get(f"/api/v1/tasks/{task_id}")
    assert get_after_delete.status_code == 404


def test_validation_422_empty_title(client):
    res = client.post(
        "/api/v1/tasks/",
        json={"title": "   ", "description": "x", "status": "todo", "priority": 1},
    )
    assert res.status_code == 422


def test_validation_422_invalid_status(client):
    res = client.post(
        "/api/v1/tasks/",
        json={"title": "Task", "description": "x", "status": "invalid", "priority": 1},
    )
    assert res.status_code == 422


def test_not_found_error_shape(client):
    res = client.get("/api/v1/tasks/999")
    assert res.status_code == 404
    body = res.json()
    assert body["error_code"] == "NOT_FOUND"
    assert "request_id" in body

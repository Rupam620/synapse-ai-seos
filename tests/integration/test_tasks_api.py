def test_tasks_crud_flow(client) -> None:
    create_resp = client.post(
        "/api/v1/tasks",
        json={"title": "My Task", "description": "desc", "status": "todo", "priority": 3},
    )
    assert create_resp.status_code == 201
    body = create_resp.json()
    task_id = body["id"]

    list_resp = client.get("/api/v1/tasks")
    assert list_resp.status_code == 200
    assert any(item["id"] == task_id for item in list_resp.json())

    get_resp = client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 200

    patch_resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "done"

    del_resp = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_resp.status_code == 204

    not_found = client.get(f"/api/v1/tasks/{task_id}")
    assert not_found.status_code == 404


def test_validation_errors(client) -> None:
    bad_create = client.post("/api/v1/tasks", json={"title": "   "})
    assert bad_create.status_code == 422

    empty_patch = client.patch("/api/v1/tasks/999", json={})
    assert empty_patch.status_code == 422

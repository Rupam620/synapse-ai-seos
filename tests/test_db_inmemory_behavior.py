def test_inmemory_persists_within_process(client):
    create = client.post(
        "/api/v1/tasks/",
        json={"title": "Task A", "description": "desc", "status": "todo", "priority": 2},
    )
    assert create.status_code == 201

    list_res = client.get("/api/v1/tasks/")
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1

import json
import logging


def test_request_id_header_present(client):
    res = client.get("/api/v1/tasks/")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers


def test_request_id_passthrough(client):
    rid = "test-request-id-123"
    res = client.get("/api/v1/tasks/", headers={"X-Request-ID": rid})
    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == rid


def test_structured_log_fields(client, caplog):
    caplog.set_level(logging.INFO)
    client.get("/api/v1/tasks/")

    parsed = []
    for record in caplog.records:
        try:
            parsed.append(json.loads(record.getMessage()))
        except Exception:
            continue

    # caplog captures pre-formatted message; fallback assert on extra fields
    has_request_log = any(getattr(r, "event", None) == "http_request" for r in caplog.records)
    assert has_request_log

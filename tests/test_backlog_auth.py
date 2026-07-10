from __future__ import annotations


def test_backlog_requires_auth(client):
    response = client.get("/backlog")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"
    detail = response.json()["detail"]
    assert detail["code"] == "missing_token"


def test_backlog_rejects_malformed_token(client):
    response = client.get("/backlog", headers={"Authorization": "Bearer"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] in {"malformed_token", "invalid_token"}


def test_backlog_allows_valid_token(client, token_factory):
    token = token_factory()
    response = client.get("/backlog", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        print("FAIL DATA:", response.status_code, response.json())
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload and payload[0]["id"] == "item-1"

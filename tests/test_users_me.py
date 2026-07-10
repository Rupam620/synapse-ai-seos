from __future__ import annotations


def test_users_me_requires_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_users_me_returns_profile(client, token_factory):
    token = token_factory(sub="user-42")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "user-42"
    assert body["authenticated"] is True
    assert body["email"] == "user@example.com"
    assert body["name"] == "Test User"
    assert body["roles"] == ["reader"]

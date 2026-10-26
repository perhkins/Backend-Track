def test_register_and_login_returns_bearer_token(client):
    registered = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "strong-password", "role": "organizer"},
    )
    assert registered.status_code == 201
    assert "password" not in registered.text

    token = client.post(
        "/auth/token",
        data={"username": "new@example.com", "password": "strong-password"},
    )
    assert token.status_code == 200
    assert token.json()["token_type"] == "bearer"
    assert token.json()["user"]["role"] == "organizer"


def test_protected_routes_reject_missing_invalid_and_spoofed_headers(client):
    assert client.post("/events", json={}).status_code == 401
    assert client.post("/events", headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert client.post(
        "/events",
        headers={"X-Role": "organizer", "X-User-Id": "spoofed"},
        json={},
    ).status_code == 401

    expired = jwt.encode(
        {"sub": "missing-user", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    assert client.post("/events", headers={"Authorization": f"Bearer {expired}"}, json={}).status_code == 401


def test_attendee_token_cannot_create_event(client):
    client.post(
        "/auth/register",
        json={"email": "attendee@example.com", "password": "strong-password", "role": "attendee"},
    )
    token = client.post(
        "/auth/token",
        data={"username": "attendee@example.com", "password": "strong-password"},
    ).json()["access_token"]
    assert client.post("/events", headers={"Authorization": f"Bearer {token}"}, json={}).status_code == 403
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)

    def override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_user(client, email, role):
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "test-password-123", "role": role},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def organizer_headers(client):
    user = register_user(client, "organizer@example.com", "organizer")
    token = client.post(
        "/auth/token",
        data={"username": user["email"], "password": "test-password-123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def attendee_headers(client):
    user = register_user(client, "attendee@example.com", "attendee")
    token = client.post(
        "/auth/token",
        data={"username": user["email"], "password": "test-password-123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def event_payload(capacity=2):
    return {
        "title": "Community Meetup",
        "description": "A useful event",
        "venue": "Room 1",
        "starts_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "capacity": capacity,
    }

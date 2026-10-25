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


@pytest.fixture
def organizer_headers():
    return {"X-Role": "organizer", "X-User-Id": "organizer-1"}


@pytest.fixture
def attendee_headers():
    return {"X-Role": "attendee", "X-User-Id": "attendee-1"}


def event_payload(capacity=2):
    return {
        "title": "Community Meetup",
        "description": "A useful event",
        "venue": "Room 1",
        "starts_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "capacity": capacity,
    }

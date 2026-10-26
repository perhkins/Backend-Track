from datetime import datetime, timedelta, timezone

from tests.conftest import event_payload


def test_event_crud_and_validation(client, organizer_headers):
    response = client.post("/events", headers=organizer_headers, json=event_payload())
    assert response.status_code == 201
    event = response.json()
    assert event["available_count"] == 2

    event_id = event["id"]
    assert client.get(f"/events/{event_id}").status_code == 200
    updated = client.patch(f"/events/{event_id}", headers=organizer_headers, json={"title": "Updated"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"
    assert client.delete(f"/events/{event_id}", headers=organizer_headers).status_code == 204
    assert client.get(f"/events/{event_id}").status_code == 404


def test_event_rejects_invalid_input_and_wrong_owner(client, organizer_headers):
    payload = event_payload()
    payload["capacity"] = 0
    assert client.post("/events", headers=organizer_headers, json=payload).status_code == 422

    payload = event_payload()
    payload["venue"] = None
    assert client.post("/events", headers=organizer_headers, json=payload).status_code == 422

    created = client.post("/events", headers=organizer_headers, json=event_payload()).json()
    wrong_owner_user = client.post(
        "/auth/register",
        json={"email": "other@example.com", "password": "test-password-123", "role": "organizer"},
    ).json()
    wrong_owner_token = client.post(
        "/auth/token",
        data={"username": wrong_owner_user["email"], "password": "test-password-123"},
    ).json()["access_token"]
    wrong_owner = {"Authorization": f"Bearer {wrong_owner_token}"}
    assert client.patch(f"/events/{created['id']}", headers=wrong_owner, json={"title": "No"}).status_code == 403


def test_event_filters(client, organizer_headers):
    response = client.post("/events", headers=organizer_headers, json=event_payload())
    starts_at = response.json()["starts_at"]
    assert client.get("/events?upcoming=true").status_code == 200
    assert client.get(f"/events?from={starts_at}&to={starts_at}").status_code == 200
    assert client.get("/events?from=2031-01-02T00:00:00Z&to=2031-01-01T00:00:00Z").status_code == 400

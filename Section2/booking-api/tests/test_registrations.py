from tests.conftest import event_payload
from tests.test_attendees import create_attendee


def setup_event(client, organizer_headers, capacity=1):
    event = client.post("/events", headers=organizer_headers, json=event_payload(capacity)).json()
    return event["id"]


def test_rsvp_duplicate_full_and_cancellation(client, organizer_headers):
    event_id = setup_event(client, organizer_headers, 1)
    first = create_attendee(client, "attendee-1").json()
    second = create_attendee(client, "attendee-2").json()
    first_headers = {"X-Role": "attendee", "X-User-Id": first["id"]}
    second_headers = {"X-Role": "attendee", "X-User-Id": second["id"]}

    assert client.post(f"/events/{event_id}/registrations", headers=first_headers).status_code == 201
    assert client.post(f"/events/{event_id}/registrations", headers=first_headers).status_code == 409
    assert client.post(f"/events/{event_id}/registrations", headers=second_headers).status_code == 201
    assert client.delete(f"/events/{event_id}/registrations/me", headers=first_headers).status_code == 204
    assert client.delete(f"/events/{event_id}/registrations/me", headers=first_headers).status_code == 404


def test_roster_and_attendee_events(client, organizer_headers):
    event_id = setup_event(client, organizer_headers, 2)
    attendee = create_attendee(client).json()
    headers = {"X-Role": "attendee", "X-User-Id": attendee["id"]}
    assert client.post(f"/events/{event_id}/registrations", headers=headers).status_code == 201
    roster = client.get(f"/events/{event_id}/registrations", headers=organizer_headers)
    assert roster.status_code == 200 and len(roster.json()) == 1
    attendee_events = client.get(f"/attendees/{attendee['id']}/events", headers=headers)
    assert attendee_events.status_code == 200 and len(attendee_events.json()) == 1


def test_waitlist_promotes_fifo(client, organizer_headers):
    event_id = setup_event(client, organizer_headers, 1)
    first = create_attendee(client, "first").json()
    second = create_attendee(client, "second").json()
    first_headers = {"X-Role": "attendee", "X-User-Id": first["id"]}
    second_headers = {"X-Role": "attendee", "X-User-Id": second["id"]}
    assert client.post(f"/events/{event_id}/registrations", headers=first_headers).status_code == 201
    waiting = client.post(f"/events/{event_id}/registrations", headers=second_headers)
    assert waiting.status_code == 201 and waiting.json()["status"] == "waiting"
    assert client.delete(f"/events/{event_id}/registrations/me", headers=first_headers).status_code == 204
    events = client.get(f"/attendees/{second['id']}/events", headers=second_headers).json()
    assert len(events) == 1

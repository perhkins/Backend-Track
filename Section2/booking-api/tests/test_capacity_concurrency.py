from concurrent.futures import ThreadPoolExecutor

from tests.conftest import event_payload
from tests.test_attendees import create_attendee


def test_capacity_never_exceeded(client, organizer_headers):
    event_id = client.post("/events", headers=organizer_headers, json=event_payload(10)).json()["id"]
    attendees = [create_attendee(client, f"concurrent-{i}").json() for i in range(100)]

    def register(attendee):
        headers = {"X-Role": "attendee", "X-User-Id": attendee["id"]}
        return client.post(f"/events/{event_id}/registrations", headers=headers).status_code

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(register, attendees))
    event = client.get(f"/events/{event_id}").json()
    assert event["registered_count"] <= event["capacity"]

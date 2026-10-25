from tests.conftest import event_payload


def create_attendee(client, user_id="attendee-1", email=None):
    return client.post(
        "/attendees",
        headers={"X-Role": "attendee", "X-User-Id": user_id},
        json={"name": "Ada Lovelace", "email": email or f"{user_id}@example.com", "phone": "123"},
    )


def test_attendee_crud_and_case_insensitive_email(client):
    headers = {"X-Role": "attendee", "X-User-Id": "attendee-1"}
    created = create_attendee(client)
    assert created.status_code == 201
    attendee_id = created.json()["id"]
    assert client.get(f"/attendees/{attendee_id}", headers=headers).status_code == 200
    assert client.patch(f"/attendees/{attendee_id}", headers=headers, json={"name": "Grace"}).json()["name"] == "Grace"
    duplicate = create_attendee(client, "attendee-2", "ATTENDEE-1@EXAMPLE.COM")
    assert duplicate.status_code == 409
    assert client.delete(f"/attendees/{attendee_id}", headers=headers).status_code == 204


def test_attendee_requires_owner_or_organizer(client):
    created = create_attendee(client).json()
    wrong = {"X-Role": "attendee", "X-User-Id": "other"}
    assert client.get(f"/attendees/{created['id']}", headers=wrong).status_code == 403

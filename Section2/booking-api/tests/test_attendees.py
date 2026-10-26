from tests.conftest import register_user

_attendee_tokens = {}


def create_attendee(client, user_id="attendee-1", email=None):
    user = register_user(client, f"{user_id}@users.example.com", "attendee")
    token = client.post(
        "/auth/token",
        data={"username": user["email"], "password": "test-password-123"},
    ).json()["access_token"]
    response = client.post(
        "/attendees",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Ada Lovelace", "email": email or f"{user_id}@example.com", "phone": "123"},
    )
    if response.status_code == 201:
        _attendee_tokens[response.json()["id"]] = token
    return response


def attendee_token_headers(client, attendee_id):
    return {"Authorization": f"Bearer {_attendee_tokens[attendee_id]}"}


def test_attendee_crud_and_case_insensitive_email(client):
    created = create_attendee(client)
    headers = attendee_token_headers(client, created.json()["id"])
    assert created.status_code == 201
    attendee_id = created.json()["id"]
    assert client.get(f"/attendees/{attendee_id}", headers=headers).status_code == 200
    assert client.patch(f"/attendees/{attendee_id}", headers=headers, json={"name": "Grace"}).json()["name"] == "Grace"
    duplicate = create_attendee(client, "attendee-2", "ATTENDEE-1@EXAMPLE.COM")
    assert duplicate.status_code == 409
    assert client.delete(f"/attendees/{attendee_id}", headers=headers).status_code == 204


def test_attendee_requires_owner_or_organizer(client):
    created = create_attendee(client).json()
    wrong_user = client.post(
        "/auth/register",
        json={"email": "other@users.example.com", "password": "test-password-123", "role": "attendee"},
    ).json()
    wrong_token = client.post(
        "/auth/token",
        data={"username": wrong_user["email"], "password": "test-password-123"},
    ).json()["access_token"]
    wrong = {"Authorization": f"Bearer {wrong_token}"}
    assert client.get(f"/attendees/{created['id']}", headers=wrong).status_code == 403

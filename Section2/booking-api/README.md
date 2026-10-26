# Event RSVP API

A locally runnable FastAPI service for organizer-managed events and attendee reservations. It uses SQLite persistence, validates event capacity, supports RSVP cancellation and FIFO waitlists, filters events by date, and exposes generated Swagger/OpenAPI documentation.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The service runs at `http://127.0.0.1:8000/`. The SQLite database is stored in `booking.db` unless `DATABASE_URL` is set.

Documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Program logic

Events and attendees are stored as relational records. A registration increments an event's `registered_count` and creates the attendee-event relationship in one database transaction. The database constraint `registered_count <= capacity` and the unique event-attendee registration constraint protect the core invariants. Cancellation decrements the count and promotes the oldest waiting entry in the same transaction.

Protected endpoints use bearer tokens. Register a user, exchange the credentials
for a token, and send `Authorization: Bearer <access-token>` with each protected
request. Roles are stored server-side and cannot be changed by request headers.
Set a strong `JWT_SECRET` environment variable outside local development.

## Example flow

The examples below send valid JSON and assume the service is running at
`http://127.0.0.1:8000`. The event date must remain in the future when you run
the command.

### PowerShell

```powershell
# Register an organizer
curl.exe -X POST "http://127.0.0.1:8000/auth/register" -H "Content-Type: application/json" --data-raw '{"email":"organizer@example.com","password":"strong-password","role":"organizer"}'

# Log in and copy the access_token from the response
curl.exe -X POST "http://127.0.0.1:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" --data-raw "username=organizer@example.com&password=strong-password"

# Create an Event
curl.exe -X POST "http://127.0.0.1:8000/events" -H "Content-Type: application/json" -H "Authorization: Bearer <organizer-access-token>" --data-raw '{"title":"API Workshop","venue":"Room 1","starts_at":"2030-01-01T10:00:00Z","capacity":2}'

# Register an attendee, log in, then create the attendee profile with that token
curl.exe -X POST "http://127.0.0.1:8000/auth/register" -H "Content-Type: application/json" --data-raw '{"email":"ada-login@example.com","password":"strong-password","role":"attendee"}'
curl.exe -X POST "http://127.0.0.1:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" --data-raw "username=ada-login@example.com&password=strong-password"
curl.exe -X POST "http://127.0.0.1:8000/attendees" -H "Content-Type: application/json" -H "Authorization: Bearer <attendee-access-token>" --data-raw '{"name":"Ada Lovelace","email":"ada@example.com"}'
```

### Bash

```bash
# Create an Event
curl.exe -X POST "http://127.0.0.1:8000/events" -H "Content-Type: application/json" -H "Authorization: Bearer <organizer-access-token>" --data-raw '{"title":"API Workshop","venue":"Room 1","starts_at":"2030-01-01T10:00:00Z","capacity":2}'

# Attendee request
curl.exe -X POST "http://127.0.0.1:8000/attendees" -H "Content-Type: application/json" -H "Authorization: Bearer <attendee-access-token>" --data-raw '{"name":"Ada Lovelace","email":"ada@example.com"}'
```

## Postman

Import `postman/event-rsvp-api.postman_collection.json` and
`postman/event-rsvp-api.postman_environment.json` into the Postman VS Code
extension. Run the register/login requests first; the collection test scripts
save tokens and IDs into the environment.

Published documentation URL: https://documenter.getpostman.com/view/59208032/2sBYHUULXN

## Testing

```powershell
pytest
```

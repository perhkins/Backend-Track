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

The development exercise uses `X-Role` and `X-User-Id` headers:

```text
X-Role: organizer
X-User-Id: organizer-1
```

or:

```text
X-Role: attendee
X-User-Id: <attendee-id>
```

These headers demonstrate role and ownership behavior; they are not production authentication.

## Example flow

The examples below send valid JSON and assume the service is running at
`http://127.0.0.1:8000`. The event date must remain in the future when you run
the command.

### PowerShell

```powershell
# Create an Event
curl.exe -X POST "http://127.0.0.1:8000/events" -H "Content-Type: application/json" -H "X-Role: organizer" -H "X-User-Id: organizer-1" --data-raw '{"title":"API Workshop","venue":"Room 1","starts_at":"2030-01-01T10:00:00Z","capacity":2}'

# Attendee request
curl.exe -X POST "http://127.0.0.1:8000/attendees" -H "Content-Type: application/json" -H "X-Role: attendee" -H "X-User-Id: attendee-1" --data-raw '{"name":"Ada Lovelace","email":"ada@example.com"}'
```

### Bash

```bash
# Create an Event
curl.exe -X POST "http://127.0.0.1:8000/events" -H "Content-Type: application/json" -H "X-Role: organizer" -H "X-User-Id: organizer-1" --data-raw '{"title":"API Workshop","venue":"Room 1","starts_at":"2030-01-01T10:00:00Z","capacity":2}'

# Attendee request
curl.exe -X POST "http://127.0.0.1:8000/attendees" -H "Content-Type: application/json" -H "X-Role: attendee" -H "X-User-Id: attendee-1" --data-raw '{"name":"Ada Lovelace","email":"ada@example.com"}'
```

## Testing

```powershell
pytest
```

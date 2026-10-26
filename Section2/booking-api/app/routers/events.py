from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models import Event, User
from app.schemas import EventCreate, EventRead, EventUpdate, RegistrationRead, WaitlistRead
from app.services import events, registrations

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED, summary="Create an event")
def create_event(data: EventCreate, db: Session = Depends(get_db), user: User = Depends(require_role("organizer"))):
    return events.event_read(events.create_event(db, user.id, data))


@router.get("", response_model=list[EventRead], summary="List events")
def list_events(
    upcoming: bool | None = Query(default=None),
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
):
    return [events.event_read(event) for event in events.list_events(db, upcoming, from_date, to_date)]


@router.get("/{event_id}", response_model=EventRead, summary="Get an event")
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return events.event_read(event)


@router.patch("/{event_id}", response_model=EventRead, summary="Update an owned event")
def update_event(event_id: str, data: EventUpdate, db: Session = Depends(get_db), user: User = Depends(require_role("organizer"))):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if event.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="organizer ownership required")
    return events.event_read(events.update_event(db, event, data))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an owned event")
def delete_event(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("organizer"))):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if event.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="organizer ownership required")
    events.delete_event(db, event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{event_id}/registrations", response_model=list[RegistrationRead], summary="View an event roster")
def get_registrations(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("organizer"))):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if event.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="organizer ownership required")
    return registrations.event_registrations(db, event_id)


@router.get("/{event_id}/waitlist", response_model=list[WaitlistRead], summary="View an event waitlist")
def get_waitlist(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("organizer"))):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if event.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="organizer ownership required")
    return registrations.event_waitlist(db, event_id)

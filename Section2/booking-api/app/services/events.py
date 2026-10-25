from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, EventStatus, Registration, RegistrationStatus
from app.schemas import EventCreate, EventUpdate


def event_read(event: Event) -> dict:
    return {
        "id": event.id,
        "organizer_id": event.organizer_id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "online_link": event.online_link,
        "starts_at": event.starts_at,
        "ends_at": event.ends_at,
        "capacity": event.capacity,
        "registered_count": event.registered_count,
        "available_count": event.capacity - event.registered_count,
        "status": event.status,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }


def create_event(db: Session, organizer_id: str, data: EventCreate) -> Event:
    event = Event(organizer_id=organizer_id, **data.model_dump())
    event.online_link = str(data.online_link) if data.online_link else None
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, upcoming: bool | None, from_date: datetime | None, to_date: datetime | None) -> list[Event]:
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="from must be before or equal to to")
    query = select(Event).order_by(Event.starts_at)
    if upcoming:
        query = query.where(Event.starts_at >= datetime.now(timezone.utc), Event.status == EventStatus.PUBLISHED.value)
    if from_date:
        query = query.where(Event.starts_at >= from_date)
    if to_date:
        query = query.where(Event.starts_at <= to_date)
    return list(db.scalars(query))


def update_event(db: Session, event: Event, data: EventUpdate) -> Event:
    values = data.model_dump(exclude_unset=True)
    if "capacity" in values and values["capacity"] < event.registered_count:
        raise HTTPException(status_code=409, detail="capacity cannot be below confirmed registrations")
    for key, value in values.items():
        if key == "online_link":
            value = str(value) if value else None
        setattr(event, key, value)
    if not event.venue and not event.online_link:
        raise HTTPException(status_code=422, detail="venue or online_link is required")
    if event.ends_at and event.ends_at <= event.starts_at:
        raise HTTPException(status_code=422, detail="ends_at must be after starts_at")
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    for registration in event.registrations:
        if registration.status == RegistrationStatus.CONFIRMED.value:
            registration.status = RegistrationStatus.CANCELLED.value
            registration.cancelled_at = datetime.now(timezone.utc)
    db.delete(event)
    db.commit()

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Attendee, Event, Registration, RegistrationStatus
from app.schemas import AttendeeCreate, AttendeeUpdate


def create_attendee(db: Session, data: AttendeeCreate, attendee_id: str | None = None) -> Attendee:
    if db.scalar(select(Attendee).where(Attendee.email == data.email.casefold())):
        raise HTTPException(status_code=409, detail="email already exists")
    attendee = Attendee(id=attendee_id, **data.model_dump())
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee


def update_attendee(db: Session, attendee: Attendee, data: AttendeeUpdate) -> Attendee:
    values = data.model_dump(exclude_unset=True)
    if "email" in values:
        existing = db.scalar(select(Attendee).where(Attendee.email == values["email"], Attendee.id != attendee.id))
        if existing:
            raise HTTPException(status_code=409, detail="email already exists")
    for key, value in values.items():
        setattr(attendee, key, value)
    db.commit()
    db.refresh(attendee)
    return attendee


def attendee_events(db: Session, attendee_id: str) -> list[Event]:
    query = (
        select(Event)
        .join(Registration, Registration.event_id == Event.id)
        .where(Registration.attendee_id == attendee_id, Registration.status == RegistrationStatus.CONFIRMED.value)
        .order_by(Event.starts_at)
    )
    return list(db.scalars(query))


def delete_attendee(db: Session, attendee: Attendee) -> None:
    for registration in attendee.registrations:
        if registration.status == RegistrationStatus.CONFIRMED.value:
            registration.status = RegistrationStatus.CANCELLED.value
    db.delete(attendee)
    db.commit()

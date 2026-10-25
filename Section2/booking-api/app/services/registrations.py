from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import Attendee, Event, EventStatus, Registration, RegistrationStatus, WaitlistEntry, WaitlistStatus


def register(db: Session, event_id: str, attendee_id: str) -> tuple[Registration | None, WaitlistEntry | None]:
    event = db.get(Event, event_id)
    attendee = db.get(Attendee, attendee_id)
    if not event or not attendee:
        raise HTTPException(status_code=404, detail="event or attendee not found")
    starts_at = event.starts_at
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)
    if event.status in {EventStatus.CANCELLED.value, EventStatus.COMPLETED.value} or starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=409, detail="event is not accepting registrations")
    existing = db.scalar(select(Registration).where(Registration.event_id == event_id, Registration.attendee_id == attendee_id))
    if existing and existing.status == RegistrationStatus.CONFIRMED.value:
        raise HTTPException(status_code=409, detail="attendee is already registered")
    if existing:
        existing.status = RegistrationStatus.CONFIRMED.value
        existing.cancelled_at = None
        if event.registered_count >= event.capacity:
            raise HTTPException(status_code=409, detail="event is full")
        event.registered_count += 1
        db.commit()
        return existing, None
    try:
        result = db.execute(
            update(Event)
            .where(
                Event.id == event_id,
                Event.registered_count < Event.capacity,
                Event.status == EventStatus.PUBLISHED.value,
            )
            .values(registered_count=Event.registered_count + 1)
        )
        if result.rowcount != 1:
            db.rollback()
            if not settings.allow_waitlist:
                raise HTTPException(status_code=409, detail="event is full")
            return None, add_waitlist(db, event_id, attendee_id)
        registration = Registration(event_id=event_id, attendee_id=attendee_id)
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration, None
    except (IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="registration conflict; please retry") from exc


def cancel_registration(db: Session, event_id: str, attendee_id: str) -> None:
    registration = db.scalar(
        select(Registration).where(
            Registration.event_id == event_id,
            Registration.attendee_id == attendee_id,
            Registration.status == RegistrationStatus.CONFIRMED.value,
        )
    )
    if not registration:
        raise HTTPException(status_code=404, detail="active registration not found")
    event = db.get(Event, event_id)
    registration.status = RegistrationStatus.CANCELLED.value
    registration.cancelled_at = datetime.now(timezone.utc)
    event.registered_count -= 1
    promote_waitlisted(db, event)
    db.commit()


def add_waitlist(db: Session, event_id: str, attendee_id: str) -> WaitlistEntry:
    existing = db.scalar(
        select(WaitlistEntry).where(
            WaitlistEntry.event_id == event_id,
            WaitlistEntry.attendee_id == attendee_id,
            WaitlistEntry.status == WaitlistStatus.WAITING.value,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="attendee is already waitlisted")
    entry = WaitlistEntry(event_id=event_id, attendee_id=attendee_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def cancel_waitlist(db: Session, event_id: str, attendee_id: str) -> None:
    entry = db.scalar(
        select(WaitlistEntry).where(
            WaitlistEntry.event_id == event_id,
            WaitlistEntry.attendee_id == attendee_id,
            WaitlistEntry.status == WaitlistStatus.WAITING.value,
        )
    )
    if not entry:
        raise HTTPException(status_code=404, detail="active waitlist entry not found")
    entry.status = WaitlistStatus.CANCELLED.value
    db.commit()


def promote_waitlisted(db: Session, event: Event) -> None:
    if event.registered_count >= event.capacity:
        return
    entry = db.scalar(
        select(WaitlistEntry)
        .where(WaitlistEntry.event_id == event.id, WaitlistEntry.status == WaitlistStatus.WAITING.value)
        .order_by(WaitlistEntry.created_at, WaitlistEntry.id)
        .limit(1)
    )
    if not entry:
        return
    entry.status = WaitlistStatus.PROMOTED.value
    entry.promoted_at = datetime.now(timezone.utc)
    registration = db.scalar(select(Registration).where(Registration.event_id == event.id, Registration.attendee_id == entry.attendee_id))
    if registration:
        registration.status = RegistrationStatus.CONFIRMED.value
        registration.cancelled_at = None
    else:
        db.add(Registration(event_id=event.id, attendee_id=entry.attendee_id))
    event.registered_count += 1


def event_registrations(db: Session, event_id: str) -> list[Registration]:
    return list(
        db.scalars(
            select(Registration)
            .options(joinedload(Registration.attendee))
            .where(Registration.event_id == event_id)
            .order_by(Registration.registered_at)
        )
    )


def event_waitlist(db: Session, event_id: str) -> list[WaitlistEntry]:
    return list(
        db.scalars(
            select(WaitlistEntry)
            .options(joinedload(WaitlistEntry.attendee))
            .where(WaitlistEntry.event_id == event_id)
            .order_by(WaitlistEntry.created_at)
        )
    )

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import Actor, require_role
from app.database import get_db
from app.models import Attendee
from app.schemas import AttendeeCreate, AttendeeRead, AttendeeUpdate, EventRead
from app.services import attendees, events

router = APIRouter(prefix="/attendees", tags=["attendees"])


def check_owner(attendee_id: str, actor: Actor, db: Session) -> Attendee:
    attendee = db.get(Attendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="attendee not found")
    if actor.role != "organizer" and actor.user_id != attendee_id:
        raise HTTPException(status_code=403, detail="attendee ownership required")
    return attendee


@router.post("", response_model=AttendeeRead, status_code=status.HTTP_201_CREATED, summary="Create an attendee")
def create_attendee(data: AttendeeCreate, db: Session = Depends(get_db), actor: Actor = Depends(require_role("attendee", "organizer"))):
    return attendees.create_attendee(db, data, actor.user_id if actor.role == "attendee" else None)


@router.get("", response_model=list[AttendeeRead], summary="List attendees")
def list_attendees(db: Session = Depends(get_db), actor: Actor = Depends(require_role("organizer"))):
    return list(db.scalars(select(Attendee).order_by(Attendee.name)))


@router.get("/{attendee_id}", response_model=AttendeeRead, summary="Get an attendee")
def get_attendee(attendee_id: str, db: Session = Depends(get_db), actor: Actor = Depends(require_role("attendee", "organizer"))):
    return check_owner(attendee_id, actor, db)


@router.patch("/{attendee_id}", response_model=AttendeeRead, summary="Update an attendee")
def update_attendee(attendee_id: str, data: AttendeeUpdate, db: Session = Depends(get_db), actor: Actor = Depends(require_role("attendee", "organizer"))):
    return attendees.update_attendee(db, check_owner(attendee_id, actor, db), data)


@router.delete("/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an attendee")
def delete_attendee(attendee_id: str, db: Session = Depends(get_db), actor: Actor = Depends(require_role("attendee", "organizer"))):
    attendees.delete_attendee(db, check_owner(attendee_id, actor, db))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{attendee_id}/events", response_model=list[EventRead], summary="List an attendee's confirmed events")
def get_attendee_events(attendee_id: str, db: Session = Depends(get_db), actor: Actor = Depends(require_role("attendee", "organizer"))):
    check_owner(attendee_id, actor, db)
    return [events.event_read(event) for event in attendees.attendee_events(db, attendee_id)]

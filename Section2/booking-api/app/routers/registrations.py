from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models import Attendee, Event, User
from app.schemas import RegistrationRead, RegistrationResult, WaitlistRead
from app.services import registrations

router = APIRouter(prefix="/events/{event_id}", tags=["registrations"])


def require_attendee(event_id: str, user: User, db: Session) -> tuple[Event, Attendee]:
    event = db.get(Event, event_id)
    attendee = db.get(Attendee, user.id)
    if not event or not attendee:
        raise HTTPException(status_code=404, detail="event or attendee not found")
    return event, attendee


@router.post("/registrations", response_model=RegistrationResult, status_code=status.HTTP_201_CREATED, summary="RSVP to an event")
def register(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("attendee"))):
    registration, waitlist = registrations.register(db, event_id, user.id)
    if waitlist:
        return RegistrationResult(status="waiting", waitlist=waitlist)
    return RegistrationResult(status="confirmed", registration=registration)


@router.delete("/registrations/me", status_code=status.HTTP_204_NO_CONTENT, summary="Cancel your RSVP")
def cancel(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("attendee"))):
    registrations.cancel_registration(db, event_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/waitlist", response_model=WaitlistRead, status_code=status.HTTP_201_CREATED, summary="Join an event waitlist")
def join_waitlist(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("attendee"))):
    event, attendee = require_attendee(event_id, user, db)
    return registrations.add_waitlist(db, event.id, attendee.id)


@router.delete("/waitlist/me", status_code=status.HTTP_204_NO_CONTENT, summary="Leave an event waitlist")
def leave_waitlist(event_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("attendee"))):
    registrations.cancel_waitlist(db, event_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Event


@dataclass(frozen=True)
class Actor:
    role: str
    user_id: str


def get_actor(
    role: str | None = Header(default=None, alias=settings.role_header),
    user_id: str | None = Header(default=None, alias=settings.user_id_header),
) -> Actor:
    if role not in {"organizer", "attendee"} or not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="valid role context is required")
    return Actor(role=role, user_id=user_id)


def require_role(*roles: str):
    def dependency(actor: Actor = Depends(get_actor)) -> Actor:
        if actor.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient role")
        return actor

    return dependency


def require_event_owner(event_id: str, actor: Actor, db: Session) -> Event:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if actor.role != "organizer" or event.organizer_id != actor.user_id:
        raise HTTPException(status_code=403, detail="organizer ownership required")
    return event

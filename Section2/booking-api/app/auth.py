from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, User, UserRole
from app.security import get_current_user


def require_role(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="insufficient role")
        return user

    return dependency


def require_event_owner(event_id: str, user: User, db: Session = Depends(get_db)) -> Event:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    if user.role != UserRole.ORGANIZER.value or event.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="organizer ownership required")
    return event

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class RegistrationStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class WaitlistStatus(str, Enum):
    WAITING = "waiting"
    PROMOTED = "promoted"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_event_capacity_positive"),
        CheckConstraint("registered_count >= 0 AND registered_count <= capacity", name="ck_event_count_capacity"),
        Index("ix_events_status_starts_at", "status", "starts_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organizer_id: Mapped[str] = mapped_column(String(36), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(300), nullable=True)
    online_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer)
    registered_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default=EventStatus.PUBLISHED.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    registrations: Mapped[list["Registration"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class Attendee(Base):
    __tablename__ = "attendees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    registrations: Mapped[list["Registration"]] = relationship(back_populates="attendee", cascade="all, delete-orphan")
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="attendee", cascade="all, delete-orphan")


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("event_id", "attendee_id", name="uq_registration_event_attendee"),
        Index("ix_registrations_event_status", "event_id", "status"),
        Index("ix_registrations_attendee_status", "attendee_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    attendee_id: Mapped[str] = mapped_column(ForeignKey("attendees.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default=RegistrationStatus.CONFIRMED.value)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event: Mapped[Event] = relationship(back_populates="registrations")
    attendee: Mapped[Attendee] = relationship(back_populates="registrations")


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"
    __table_args__ = (
        UniqueConstraint("event_id", "attendee_id", name="uq_waitlist_event_attendee"),
        Index("ix_waitlist_event_status_created", "event_id", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    attendee_id: Mapped[str] = mapped_column(ForeignKey("attendees.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default=WaitlistStatus.WAITING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    promoted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event: Mapped[Event] = relationship(back_populates="waitlist_entries")
    attendee: Mapped[Attendee] = relationship(back_populates="waitlist_entries")

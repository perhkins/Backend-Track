from datetime import datetime, timezone
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models import EventStatus, RegistrationStatus, WaitlistStatus


def trim(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("value must not be blank")
    return value


def aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value.astimezone(timezone.utc)


class ErrorResponse(BaseModel):
    error: str
    detail: str


class UserRegister(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(min_length=8, max_length=128)
    role: Literal["organizer", "attendee"]

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = trim(value)
        if "@" not in value:
            raise ValueError("email must be valid")
        return value.casefold()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserRead


class EventCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str | None = None
    venue: str | None = Field(default=None, max_length=300)
    online_link: AnyHttpUrl | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    capacity: int = Field(gt=0)

    @field_validator("title", "venue", mode="before")
    @classmethod
    def normalize_text(cls, value):
        return trim(value) if value is not None else value

    @field_validator("starts_at", "ends_at")
    @classmethod
    def validate_timezone(cls, value):
        return aware(value) if value else value

    @model_validator(mode="after")
    def validate_location_and_times(self):
        if not self.venue and not self.online_link:
            raise ValueError("venue or online_link is required")
        if self.starts_at <= datetime.now(timezone.utc):
            raise ValueError("starts_at must be in the future")
        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    venue: str | None = Field(default=None, max_length=300)
    online_link: AnyHttpUrl | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    capacity: int | None = Field(default=None, gt=0)
    status: Literal["draft", "published", "cancelled", "completed"] | None = None

    @field_validator("title", "venue", mode="before")
    @classmethod
    def normalize_optional_text(cls, value):
        return trim(value) if value is not None else value

    @field_validator("starts_at", "ends_at")
    @classmethod
    def validate_optional_timezone(cls, value):
        return aware(value) if value else value


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organizer_id: str
    title: str
    description: str | None
    venue: str | None
    online_link: str | None
    starts_at: datetime
    ends_at: datetime | None
    capacity: int
    registered_count: int
    available_count: int
    status: EventStatus
    created_at: datetime
    updated_at: datetime


class AttendeeCreate(BaseModel):
    name: str = Field(max_length=200)
    email: str = Field(max_length=320)
    phone: str | None = Field(default=None, max_length=50)

    @field_validator("name", "email", "phone", mode="before")
    @classmethod
    def normalize(cls, value):
        return trim(value) if value is not None else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        if "@" not in value:
            raise ValueError("email must be valid")
        return value.casefold()


class AttendeeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=50)

    @field_validator("name", "email", "phone", mode="before")
    @classmethod
    def normalize(cls, value):
        return trim(value) if value is not None else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        if "@" not in value:
            raise ValueError("email must be valid")
        return value.casefold()


class AttendeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: str | None
    created_at: datetime
    updated_at: datetime


class RegistrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    attendee_id: str
    status: RegistrationStatus
    registered_at: datetime
    cancelled_at: datetime | None
    attendee: AttendeeRead | None = None


class WaitlistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    attendee_id: str
    status: WaitlistStatus
    created_at: datetime
    promoted_at: datetime | None
    attendee: AttendeeRead | None = None


class RegistrationResult(BaseModel):
    registration: RegistrationRead | None = None
    waitlist: WaitlistRead | None = None
    status: Literal["confirmed", "waiting"]


class EventWithRegistrations(EventRead):
    registrations: list[RegistrationRead]


class AttendeeWithEvents(AttendeeRead):
    events: list[EventRead]

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./booking.db")
    role_header: str = "X-Role"
    user_id_header: str = "X-User-Id"
    allow_waitlist: bool = os.getenv("ALLOW_WAITLIST", "true").lower() == "true"


settings = Settings()

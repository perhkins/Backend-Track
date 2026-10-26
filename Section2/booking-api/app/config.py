from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./booking.db")
    allow_waitlist: bool = os.getenv("ALLOW_WAITLIST", "true").lower() == "true"
    jwt_secret: str = os.getenv("JWT_SECRET", "local-development-secret-change-me")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    jwt_algorithm: str = "HS256"


settings = Settings()

import logging

from fastapi import FastAPI

from app.database import init_db
from app.routers import attendees, auth, events, registrations

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Event RSVP API",
        version="1.0.0",
        description="Event management and capacity-safe attendee registration API using bearer-token authentication.",
    )

    @app.on_event("startup")
    def startup() -> None:
        init_db()

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok"}

    @app.get("/", tags=["system"], summary="API entry point")
    def root():
        return {
            "name": "Event RSVP API",
            "status": "ok",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
        }

    app.include_router(events.router)
    app.include_router(attendees.router)
    app.include_router(registrations.router)
    app.include_router(auth.router)
    return app


app = create_app()

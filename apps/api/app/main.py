from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.routes import actions, alerts, contacts, health, places, preferences, voice

setup_logging()
settings = get_settings()

app = FastAPI(title="Haven API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(places.router, prefix="/places", tags=["places"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(actions.router, prefix="/actions", tags=["actions"])

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.routes import sessions, workers, approvals, livekit, voice, openclaw, events

setup_logging()
settings = get_settings()

app = FastAPI(title="Haven API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(workers.router, prefix="/workers", tags=["workers"])
app.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
app.include_router(livekit.router, prefix="/livekit", tags=["livekit"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(openclaw.router, prefix="/openclaw", tags=["openclaw"])
app.include_router(events.router, prefix="/events", tags=["events"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "haven-api"}

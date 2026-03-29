"""
OpenClaw Gateway — thin HTTP bridge between Haven API and OpenClaw.

Haven API sends natural language instructions here.
This gateway forwards them to OpenClaw (running on localhost:18789).
OpenClaw handles all browser/desktop automation autonomously.

Start with:
    cd apps/openclaw-gateway
    uvicorn app.main:app --reload --port 9090
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import registration
from app.routes import execute, health, screen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        worker_id = await registration.register()
        registration.start_heartbeat()
        logger.info("Registered with Haven API as worker %s", worker_id)
    except Exception as exc:
        logger.warning(
            "Could not register with Haven API (%s). "
            "Gateway will run standalone — register manually or start the API first.",
            exc,
        )

    yield

    await registration.mark_offline()


app = FastAPI(title="OpenClaw Gateway", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(execute.router, tags=["execute"])
app.include_router(screen.router, tags=["screen"])

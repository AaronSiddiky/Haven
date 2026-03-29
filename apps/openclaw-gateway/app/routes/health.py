from fastapi import APIRouter

from app.openclaw import health_check

router = APIRouter()


@router.get("/health")
async def health():
    openclaw_status = await health_check()
    return {
        "status": "ok",
        "gateway": "running",
        "openclaw": openclaw_status,
    }

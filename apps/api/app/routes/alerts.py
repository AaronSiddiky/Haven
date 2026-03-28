from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.core.errors import NotFoundError
from app.db.repositories import alert_repository
from app.services import alert_matcher
from app.services.official_guidance_service import guidance_for_alert

router = APIRouter()


@router.get("/active")
async def get_active_alerts(
    user_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    """
    Get active alerts, optionally filtered to a user's monitored places.
    """
    if user_id:
        alerts = alert_matcher.alerts_for_user(user_id)
    else:
        alerts = alert_repository.get_active_alerts(limit=100)

    if severity:
        _order = ["clear", "inform", "watch", "warning", "act_now"]
        if severity in _order:
            min_idx = _order.index(severity)
            alerts = [a for a in alerts if _order.index(a.get("severity", "inform")) >= min_idx]

    return {"count": len(alerts), "alerts": alerts}


@router.get("/history")
async def get_alert_history(
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    alerts = alert_repository.get_active_alerts(limit=limit)
    return {"count": len(alerts), "alerts": alerts}


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    alert = alert_repository.get_alert(alert_id)
    if not alert:
        raise NotFoundError("Alert", alert_id)
    return alert


@router.get("/{alert_id}/guidance")
async def get_alert_guidance(alert_id: str):
    alert = alert_repository.get_alert(alert_id)
    if not alert:
        raise NotFoundError("Alert", alert_id)
    return guidance_for_alert(alert)

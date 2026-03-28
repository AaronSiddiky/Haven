"""
Explicit action endpoints (called from UI approval flow, not the voice agent directly).
"""
from fastapi import APIRouter, Header, HTTPException
from typing import Any, Dict

from app.core.errors import NotFoundError
from app.db.repositories import action_repository, user_repository, alert_repository
from app.integrations import twilio_client, openclaw_client
from app.schemas.actions import ApproveActionRequest, CallContactRequest, OpenGuidanceRequest
from app.services.official_guidance_service import guidance_for_alert

router = APIRouter()


@router.post("/call-contact", status_code=202)
async def call_contact(body: CallContactRequest, x_user_id: str = Header(...)):
    contact = user_repository.get_contact(str(body.contact_id))
    if not contact or contact.get("user_id") != x_user_id:
        raise NotFoundError("Contact", str(body.contact_id))

    alert_context = ""
    if body.alert_id:
        alert = alert_repository.get_alert(str(body.alert_id))
        if alert:
            alert_context = f" — {alert.get('headline', '')} ({alert.get('location_label', '')})"

    sms_body = body.message or f"Emergency alert{alert_context}. Please check in."

    log = action_repository.create(
        x_user_id,
        "call_contact",
        {"contact_id": str(body.contact_id), "message": sms_body},
        requires_approval=False,
    )

    try:
        result = await twilio_client.send_sms(to=contact["phone"], body=sms_body)
        action_repository.update_status(log["id"], "completed", result)
        return {"status": "sent", "action_id": log["id"], **result}
    except Exception as exc:
        action_repository.update_status(log["id"], "failed", {"error": str(exc)})
        raise HTTPException(status_code=502, detail=str(exc))


@router.post("/open-guidance", status_code=202)
async def open_guidance(body: OpenGuidanceRequest, x_user_id: str = Header(...)):
    alert = alert_repository.get_alert(str(body.alert_id))
    if not alert:
        raise NotFoundError("Alert", str(body.alert_id))

    guidance = guidance_for_alert(alert)
    url = guidance["guidance_url"]

    log = action_repository.create(
        x_user_id,
        "open_guidance",
        {"alert_id": str(body.alert_id), "url": url},
        requires_approval=False,
    )

    try:
        result = await openclaw_client.open_url(url, session_id=body.session_id or "")
        action_repository.update_status(log["id"], "completed", result)
        return {"status": "opened", "action_id": log["id"], "url": url, **result}
    except Exception as exc:
        action_repository.update_status(log["id"], "failed", {"error": str(exc)})
        return {"status": "error", "action_id": log["id"], "url": url, "message": str(exc)}


@router.post("/approve")
async def approve_action(body: ApproveActionRequest, x_user_id: str = Header(...)):
    action = action_repository.get(str(body.action_id))
    if not action or action.get("user_id") != x_user_id:
        raise NotFoundError("Action", str(body.action_id))
    return action_repository.approve(str(body.action_id), approved=True)


@router.post("/deny")
async def deny_action(body: ApproveActionRequest, x_user_id: str = Header(...)):
    action = action_repository.get(str(body.action_id))
    if not action or action.get("user_id") != x_user_id:
        raise NotFoundError("Action", str(body.action_id))
    return action_repository.approve(str(body.action_id), approved=False)


@router.get("/history")
def action_history(x_user_id: str = Header(...)):
    return action_repository.list_for_user(x_user_id)

"""
Watchtower endpoints — receive tweet-based alerts and broadcast to all SSE clients.

POST /watchtower/alert    — called by the worker when an urgent tweet is detected
POST /watchtower/simulate — manual demo trigger (classifies inline, then broadcasts)
"""
import json
import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.ws.manager import event_manager

logger = logging.getLogger(__name__)
router = APIRouter()


class AlertPayload(BaseModel):
    source_user: str
    content: str
    summary: str
    urgency: str = "emergency"


class SimulatePayload(BaseModel):
    content: str
    source_user: str = "demo_account"


@router.post("/alert")
async def watchtower_alert(body: AlertPayload):
    logger.info("Watchtower alert from @%s: %s", body.source_user, body.summary)
    await event_manager.broadcast("watchtower.alert", {
        "source_user": body.source_user,
        "content": body.content,
        "summary": body.summary,
        "urgency": body.urgency,
    })
    return {"status": "broadcast_sent"}


@router.post("/simulate")
async def watchtower_simulate(body: SimulatePayload):
    """
    Classify the tweet text inline with OpenAI, then broadcast if urgent.
    Always broadcasts for demo purposes regardless of classification.
    """
    settings = get_settings()
    summary = body.content[:120]

    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=120,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You classify tweets for urgency. Given a tweet, respond ONLY with "
                            'valid JSON: {"urgent": true/false, "summary": "<1-sentence summary>"}'
                        ),
                    },
                    {"role": "user", "content": body.content},
                ],
            )
            raw = resp.choices[0].message.content or "{}"
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
            result = json.loads(raw)
            summary = result.get("summary", summary)
        except Exception as exc:
            logger.error("Simulate classification failed: %s", exc)

    await event_manager.broadcast("watchtower.alert", {
        "source_user": body.source_user,
        "content": body.content,
        "summary": summary,
        "urgency": "emergency",
    })
    return {"status": "simulated", "summary": summary}

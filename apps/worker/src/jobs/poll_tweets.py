"""
Job: poll_tweets (Watchtower)

Polls a target Twitter user's latest tweets via RapidAPI twitter-api47,
classifies each new tweet for urgency using OpenAI, and fires a
POST /watchtower/alert to the Haven API when an emergency is detected.
"""
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from openai import AsyncOpenAI

from src.settings import get_settings

logger = logging.getLogger(__name__)

RAPIDAPI_HOST = "twitter-api47.p.rapidapi.com"
USER_LOOKUP_URL = f"https://{RAPIDAPI_HOST}/v3/user/by-username"
USER_TWEETS_URL = f"https://{RAPIDAPI_HOST}/v3/user/tweets"

_last_seen_tweet_id: Optional[str] = None
_cached_user_id: Optional[str] = None

CLASSIFY_SYSTEM = (
    "You are a threat-classification model. Given a tweet, decide if it describes "
    "a real, imminent geopolitical emergency, military conflict, natural disaster, "
    "or safety threat that would require someone to take immediate protective action "
    "(e.g. shelter, evacuate, power down). Respond ONLY with valid JSON: "
    '{"urgent": true/false, "summary": "<1-sentence summary>"}'
)


async def run() -> None:
    global _last_seen_tweet_id
    settings = get_settings()

    if not settings.rapidapi_key or not settings.twitter_target_username:
        return

    try:
        tweets = await _fetch_tweets(settings)
    except Exception as exc:
        logger.error("Tweet fetch failed: %s", exc)
        return

    if not tweets:
        return

    new_tweets = _filter_new(tweets)
    if not new_tweets:
        return

    _last_seen_tweet_id = new_tweets[0]["id"]

    for tweet in new_tweets:
        text = tweet.get("text", "")
        author = tweet.get("author", {}).get("username", settings.twitter_target_username)

        try:
            classification = await _classify(text, settings.openai_api_key)
        except Exception as exc:
            logger.error("Classification failed for tweet %s: %s", tweet["id"], exc)
            continue

        if classification.get("urgent"):
            logger.info(
                "URGENT tweet detected from @%s: %s",
                author,
                classification.get("summary", text[:80]),
            )
            await _fire_alert(
                settings.haven_api_url,
                source_user=author,
                content=text,
                summary=classification.get("summary", ""),
            )
        else:
            logger.debug("Non-urgent tweet from @%s: %s", author, text[:60])


async def _resolve_user_id(settings) -> str:
    global _cached_user_id
    if _cached_user_id:
        return _cached_user_id
    headers = {
        "x-rapidapi-key": settings.rapidapi_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            USER_LOOKUP_URL,
            headers=headers,
            params={"username": settings.twitter_target_username},
        )
        resp.raise_for_status()
        data = resp.json()
    uid = data.get("data", {}).get("id")
    if not uid:
        raise ValueError(f"Could not resolve user ID for @{settings.twitter_target_username}")
    _cached_user_id = uid
    logger.info("Resolved @%s → user ID %s", settings.twitter_target_username, uid)
    return uid


async def _fetch_tweets(settings) -> List[Dict[str, Any]]:
    user_id = await _resolve_user_id(settings)
    headers = {
        "x-rapidapi-key": settings.rapidapi_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            USER_TWEETS_URL,
            headers=headers,
            params={"userId": user_id},
        )
        resp.raise_for_status()
        data = resp.json()
    return data.get("data", [])


def _filter_new(tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    global _last_seen_tweet_id
    if _last_seen_tweet_id is None:
        return tweets[:1]
    new = []
    for t in tweets:
        if t["id"] == _last_seen_tweet_id:
            break
        new.append(t)
    return new


async def _classify(text: str, api_key: str) -> Dict[str, Any]:
    client = AsyncOpenAI(api_key=api_key)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=120,
        messages=[
            {"role": "system", "content": CLASSIFY_SYSTEM},
            {"role": "user", "content": text},
        ],
    )
    raw = resp.choices[0].message.content or "{}"
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(raw)


async def _fire_alert(api_url: str, source_user: str, content: str, summary: str) -> None:
    url = f"{api_url.rstrip('/')}/watchtower/alert"
    payload = {
        "source_user": source_user,
        "content": content,
        "summary": summary,
        "urgency": "emergency",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code < 300:
            logger.info("Watchtower alert fired successfully")
        else:
            logger.error("Watchtower alert failed (%d): %s", resp.status_code, resp.text)

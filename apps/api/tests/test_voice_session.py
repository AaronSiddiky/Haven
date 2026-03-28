"""
Test 1: Voice session minting.

Run with:
    cd apps/api
    python -m pytest tests/test_voice_session.py -v

Prerequisites:
    - Haven API running at localhost:8000
    - OPENAI_API_KEY set in .env (real API call — ephemeral tokens are free)
    - SUPABASE_URL and SUPABASE_SERVICE_KEY set in .env
"""
import pytest
import httpx

API_URL = "http://localhost:8000"


def _is_api_running() -> bool:
    try:
        resp = httpx.get(f"{API_URL}/health", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _is_api_running(),
    reason="Haven API not running at localhost:8000",
)


def test_voice_session_mint():
    """POST /voice/session returns session_id, client_secret, model, expires_at."""
    resp = httpx.post(
        f"{API_URL}/voice/session",
        json={"user_id": "test-user"},
        timeout=25.0,
    )
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()

    assert data.get("session_id"), "Missing session_id"
    assert data.get("client_secret"), "Missing client_secret"
    assert data.get("model"), "Missing model"
    assert data.get("expires_at"), "Missing expires_at"


def test_voice_tool_result_missing_tool():
    """POST /voice/tool-result with empty tool_name returns 400."""
    resp = httpx.post(
        f"{API_URL}/voice/tool-result",
        json={"tool_name": "", "arguments": {}, "call_id": "test"},
        timeout=10.0,
    )
    assert resp.status_code == 400


def test_create_session():
    """POST /sessions creates a session with a LiveKit room name."""
    resp = httpx.post(f"{API_URL}/sessions", timeout=10.0)
    assert resp.status_code == 201
    data = resp.json()
    assert data.get("id")
    assert data.get("livekit_room_name", "").startswith("haven-")
    assert data.get("status") == "pending"


def test_worker_registration():
    """Test 4: POST /workers/register and GET /workers/{id}."""
    reg_resp = httpx.post(
        f"{API_URL}/workers/register",
        json={
            "label": "test-worker",
            "machine_name": "test-machine",
            "gateway_url": "http://localhost:9999",
        },
        timeout=10.0,
    )
    assert reg_resp.status_code == 201
    worker = reg_resp.json()
    worker_id = worker["id"]
    assert worker["label"] == "test-worker"
    assert worker["status"] == "idle"

    get_resp = httpx.get(f"{API_URL}/workers/{worker_id}", timeout=5.0)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == worker_id


def test_heartbeat():
    """Worker heartbeat updates last_seen_at."""
    reg = httpx.post(
        f"{API_URL}/workers/register",
        json={
            "label": "heartbeat-test",
            "machine_name": "test",
            "gateway_url": "http://localhost:9998",
        },
        timeout=10.0,
    )
    worker_id = reg.json()["id"]

    beat = httpx.post(
        f"{API_URL}/workers/heartbeat",
        json={"worker_id": worker_id},
        timeout=5.0,
    )
    assert beat.status_code == 200
    assert beat.json().get("last_seen_at")

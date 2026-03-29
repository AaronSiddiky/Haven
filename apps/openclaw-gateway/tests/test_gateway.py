"""
Gateway integration tests.

Run with:
    cd apps/openclaw-gateway
    python -m pytest tests/test_gateway.py -v

Prerequisites:
    - Gateway running on localhost:9090
    - OpenClaw running on localhost:18789
"""
import pytest
import httpx

GATEWAY_URL = "http://localhost:9090"


def _is_gateway_running() -> bool:
    try:
        resp = httpx.get(f"{GATEWAY_URL}/health", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _is_gateway_running(),
    reason="Gateway not running at localhost:9090",
)


def test_health():
    """Health endpoint returns ok with OpenClaw connectivity status."""
    resp = httpx.get(f"{GATEWAY_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "openclaw" in data


def test_execute_instruction():
    """Sending an instruction forwards it to OpenClaw."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"instruction": "What time is it?"},
        timeout=60.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["run_id"]


def test_execute_empty_instruction():
    """Empty instruction returns 400."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"instruction": ""},
        timeout=5.0,
    )
    assert resp.status_code == 400


def test_get_run():
    """Completed runs are queryable via GET /runs/{id}."""
    create_resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"instruction": "Say hello"},
        timeout=60.0,
    )
    run_id = create_resp.json()["run_id"]
    resp = httpx.get(f"{GATEWAY_URL}/runs/{run_id}", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"

"""
Gateway integration tests.

Run with:
    cd apps/openclaw-gateway
    python -m pytest tests/test_gateway.py -v

Prerequisites:
    - No other services need to be running
    - Playwright browsers must be installed: playwright install chromium
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
    """Test 3a: Health endpoint returns ok with browser status."""
    resp = httpx.get(f"{GATEWAY_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["browser"] in ("running", "stopped")


def test_execute_open_url():
    """Test 3b: open_url tool navigates the browser."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"tool": "open_url", "params": {"url": "https://example.com"}},
        timeout=30.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["run_id"]
    assert "example.com" in data.get("url", "")


def test_execute_search():
    """Test 3c: search tool performs a Google search."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"tool": "search", "params": {"query": "test query"}},
        timeout=30.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["run_id"]


def test_execute_screenshot():
    """Screenshot tool returns base64 PNG."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"tool": "screenshot", "params": {}},
        timeout=15.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data.get("screenshot_base64")
    assert data.get("format") == "png"


def test_execute_unknown_tool():
    """Unknown tool returns 400."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"tool": "nonexistent", "params": {}},
        timeout=5.0,
    )
    assert resp.status_code == 400


def test_get_run():
    """Completed runs are queryable via GET /runs/{id}."""
    create_resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={"tool": "open_url", "params": {"url": "https://example.com"}},
        timeout=30.0,
    )
    run_id = create_resp.json()["run_id"]
    resp = httpx.get(f"{GATEWAY_URL}/runs/{run_id}", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"


def test_execute_task():
    """execute_task tool processes natural language instructions."""
    resp = httpx.post(
        f"{GATEWAY_URL}/execute",
        json={
            "tool": "execute_task",
            "params": {"instruction": "open https://example.com"},
        },
        timeout=30.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"

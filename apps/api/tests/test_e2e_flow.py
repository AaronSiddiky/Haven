"""
End-to-end integration tests for the Haven pipeline.

Run with:
    cd apps/api
    python -m pytest tests/test_e2e_flow.py -v

Prerequisites:
    - Haven API at localhost:8000
    - OpenClaw Gateway at localhost:9090
    - OPENCLAW_GATEWAY_URL=http://localhost:9090 in API .env
"""
import time

import pytest
import httpx

API_URL = "http://localhost:8000"
GATEWAY_URL = "http://localhost:9090"


def _services_running() -> bool:
    try:
        api = httpx.get(f"{API_URL}/health", timeout=2.0).status_code == 200
        gw = httpx.get(f"{GATEWAY_URL}/health", timeout=2.0).status_code == 200
        return api and gw
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _services_running(),
    reason="Both API and gateway must be running",
)


class TestE2EFlow:
    """Tests 4-8: Full pipeline validation."""

    def test_gateway_registered_as_worker(self):
        """Test 4: The gateway auto-registered with the API on startup."""
        # The gateway registers on startup — check via screen/config
        config = httpx.get(f"{GATEWAY_URL}/screen/config", timeout=5.0).json()
        worker_id = config.get("worker_id")
        if not worker_id:
            pytest.skip("Gateway did not register (API may not have been running at gateway startup)")

        resp = httpx.get(f"{API_URL}/workers/{worker_id}", timeout=5.0)
        assert resp.status_code == 200
        worker = resp.json()
        assert worker["gateway_url"] == f"http://localhost:9090"

    def test_session_and_livekit_tokens(self):
        """Test 5: Create session, get LiveKit tokens for both roles."""
        session = httpx.post(f"{API_URL}/sessions", timeout=10.0).json()
        session_id = session["id"]
        assert session["livekit_room_name"]

        # Operator token (subscriber)
        op = httpx.post(
            f"{API_URL}/livekit/operator-token",
            json={"session_id": session_id},
            timeout=10.0,
        )
        if op.status_code == 200:
            op_data = op.json()
            assert op_data.get("token")
            assert op_data.get("room_name")
        else:
            pytest.skip("LiveKit not configured (keys missing)")

        # Worker token (publisher)
        wk = httpx.post(
            f"{API_URL}/livekit/worker-token",
            json={"session_id": session_id},
            timeout=10.0,
        )
        assert wk.status_code == 200
        wk_data = wk.json()
        assert wk_data.get("token")

    def test_tool_dispatch_to_gateway(self):
        """Test 7 (partial): API dispatches execute_computer_task to gateway."""
        resp = httpx.post(
            f"{API_URL}/voice/tool-result",
            json={
                "tool_name": "execute_computer_task",
                "arguments": {
                    "instruction": "open https://example.com",
                    "session_id": "test",
                },
                "call_id": "e2e-test-1",
            },
            timeout=35.0,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["call_id"] == "e2e-test-1"
        assert data["tool_name"] == "execute_computer_task"
        result = data.get("result", {})
        assert result.get("status") in ("executed", "error")

    def test_sse_events(self):
        """SSE endpoint streams events for a session."""
        session = httpx.post(f"{API_URL}/sessions", timeout=10.0).json()
        session_id = session["id"]

        with httpx.stream(
            "GET",
            f"{API_URL}/events/{session_id}",
            timeout=30.0,
        ) as resp:
            assert resp.status_code == 200
            # Read at least the first event (should be a ping within 25s)
            for line in resp.iter_lines():
                if line.startswith("data:"):
                    import json
                    event = json.loads(line[5:].strip())
                    assert "type" in event
                    break

    def test_latency_open_url(self):
        """Test 8: Measure latency for gateway open_url via direct call."""
        t0 = time.monotonic()
        resp = httpx.post(
            f"{GATEWAY_URL}/execute",
            json={"tool": "open_url", "params": {"url": "https://example.com"}},
            timeout=30.0,
        )
        t1 = time.monotonic()
        elapsed_ms = (t1 - t0) * 1000

        assert resp.status_code == 200
        # Target: gateway execute should complete within 5 seconds
        assert elapsed_ms < 5000, f"open_url took {elapsed_ms:.0f}ms (target <5000ms)"
        print(f"\n  open_url latency: {elapsed_ms:.0f}ms")

    def test_latency_tool_dispatch(self):
        """Test 8: Measure latency for API→gateway tool dispatch."""
        t0 = time.monotonic()
        resp = httpx.post(
            f"{API_URL}/voice/tool-result",
            json={
                "tool_name": "execute_computer_task",
                "arguments": {"instruction": "open https://example.com"},
                "call_id": "latency-test",
            },
            timeout=35.0,
        )
        t1 = time.monotonic()
        elapsed_ms = (t1 - t0) * 1000

        assert resp.status_code == 200
        # Target: full API→gateway round trip under 6 seconds
        assert elapsed_ms < 6000, f"Tool dispatch took {elapsed_ms:.0f}ms (target <6000ms)"
        print(f"\n  API→gateway dispatch latency: {elapsed_ms:.0f}ms")

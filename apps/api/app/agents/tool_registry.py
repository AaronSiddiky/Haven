"""
OpenAI function-calling tool definitions for the Haven voice agent.

Each entry here maps 1:1 to a handler in tool_handlers/.
The registry is imported by the voice route to pass tools to the
OpenAI Realtime session and to dispatch tool calls server-side.
"""
from typing import Any, Callable, Dict, List

from app.agents.tool_handlers import (
    call_emergency_contact,
    execute_computer_task,
    explain_why_alerted,
    get_active_alerts,
    open_evacuation_page,
    read_official_guidance,
    update_monitoring_preferences,
)

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "name": "get_active_alerts",
        "description": (
            "Return the current active emergency alerts relevant to the user's monitored places. "
            "Use this when the user asks what's happening, what alerts are active, or whether "
            "there is anything they should know about."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the current user.",
                },
                "severity_filter": {
                    "type": "string",
                    "enum": ["all", "watch", "warning", "act_now"],
                    "description": "Minimum severity level to include. Default: 'all'.",
                },
            },
            "required": ["user_id"],
        },
    },
    {
        "type": "function",
        "name": "read_official_guidance",
        "description": (
            "Fetch and return the official guidance and recommended actions for a specific alert. "
            "Use this when the user asks what they should do, or wants more details about an alert."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "alert_id": {
                    "type": "string",
                    "description": "The ID of the alert to get guidance for.",
                },
            },
            "required": ["alert_id"],
        },
    },
    {
        "type": "function",
        "name": "open_evacuation_page",
        "description": (
            "Open the official evacuation page or guidance website for an alert on the remote browser. "
            "REQUIRES USER APPROVAL before executing. Use when the user asks to open guidance, "
            "see the evacuation route, or find official instructions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "alert_id": {
                    "type": "string",
                    "description": "The alert to open guidance for.",
                },
                "session_id": {
                    "type": "string",
                    "description": "The current Haven session ID.",
                },
            },
            "required": ["alert_id"],
        },
    },
    {
        "type": "function",
        "name": "call_emergency_contact",
        "description": (
            "Initiate a phone call or send an SMS to one of the user's emergency contacts. "
            "REQUIRES USER APPROVAL before executing. "
            "Use when the user asks to call or message someone."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "contact_id": {
                    "type": "string",
                    "description": "The ID of the emergency contact to reach.",
                },
                "message": {
                    "type": "string",
                    "description": "Message to include in the call/SMS.",
                },
                "alert_id": {
                    "type": "string",
                    "description": "Optional alert ID for context.",
                },
            },
            "required": ["contact_id"],
        },
    },
    {
        "type": "function",
        "name": "explain_why_alerted",
        "description": (
            "Explain in plain language why the user received a specific alert — "
            "which of their monitored places was affected and why the severity was assigned. "
            "Use when the user asks 'why am I seeing this?' or 'what does this mean for me?'"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "alert_id": {
                    "type": "string",
                    "description": "The alert to explain.",
                },
                "user_id": {
                    "type": "string",
                    "description": "The current user ID.",
                },
            },
            "required": ["alert_id", "user_id"],
        },
    },
    {
        "type": "function",
        "name": "update_monitoring_preferences",
        "description": (
            "Update the user's alert monitoring preferences, such as minimum severity level "
            "for notifications, or whether to be interrupted during active voice sessions. "
            "Use when the user says things like 'only alert me for warnings' or 'stop notifying me for watches'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The current user ID.",
                },
                "minimum_severity": {
                    "type": "string",
                    "enum": ["inform", "watch", "warning", "act_now"],
                    "description": "Minimum severity to trigger alerts.",
                },
                "voice_interruptions": {
                    "type": "boolean",
                    "description": "Whether the assistant can interrupt during voice to notify of new alerts.",
                },
            },
            "required": ["user_id"],
        },
    },
    {
        "type": "function",
        "name": "execute_computer_task",
        "description": (
            "Execute a task on the user's computer using the remote browser agent (OpenClaw). "
            "Use this for any general web browsing, searching, form filling, information "
            "retrieval, or other browser-based task the user requests. Examples: "
            "'open wikipedia', 'search for weather in NYC', 'go to nytimes.com'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "Natural language description of what to do on the computer.",
                },
                "session_id": {
                    "type": "string",
                    "description": "The current Haven session ID.",
                },
            },
            "required": ["instruction"],
        },
    },
]

HANDLER_MAP: Dict[str, Callable] = {
    "get_active_alerts": get_active_alerts.handle,
    "read_official_guidance": read_official_guidance.handle,
    "open_evacuation_page": open_evacuation_page.handle,
    "call_emergency_contact": call_emergency_contact.handle,
    "explain_why_alerted": explain_why_alerted.handle,
    "update_monitoring_preferences": update_monitoring_preferences.handle,
    "execute_computer_task": execute_computer_task.handle,
}


async def dispatch(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Route a tool call to the correct handler."""
    handler = HANDLER_MAP.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}
    return await handler(arguments)

from datetime import datetime
from src.integrations.incidents import get_incidents, get_ongoing_incidents
from src.integrations.deployments import get_deployments
from src.integrations.tickets import get_open_tickets, get_high_priority_tickets
from src.integrations.slack_client import slack_client

TOOL_DEFINITIONS = [
    {
        "name": "get_incidents",
        "description": "Fetch incidents that occurred during the specified shift period. Returns incidents created, updated, or still ongoing within the timeframe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shift_start": {
                    "type": "string",
                    "description": "ISO 8601 datetime for shift start (e.g., 2026-01-14T09:00:00Z)",
                },
                "shift_end": {
                    "type": "string",
                    "description": "ISO 8601 datetime for shift end (e.g., 2026-01-14T17:00:00Z)",
                },
            },
            "required": ["shift_start", "shift_end"],
        },
    },
    {
        "name": "get_ongoing_incidents",
        "description": "Fetch all currently unresolved incidents that require attention from the incoming engineer.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_deployments",
        "description": "Fetch deployments that occurred during the specified shift period.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shift_start": {
                    "type": "string",
                    "description": "ISO 8601 datetime for shift start",
                },
                "shift_end": {
                    "type": "string",
                    "description": "ISO 8601 datetime for shift end",
                },
            },
            "required": ["shift_start", "shift_end"],
        },
    },
    {
        "name": "get_open_tickets",
        "description": "Fetch all open tickets that may require attention.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_high_priority_tickets",
        "description": "Fetch only urgent and high priority open tickets.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_slack_threads",
        "description": "Fetch relevant Slack discussion threads from the shift period.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "Slack channel to fetch threads from (e.g., #incidents)",
                },
                "since": {
                    "type": "string",
                    "description": "ISO 8601 datetime to fetch threads since",
                },
            },
            "required": ["channel", "since"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_incidents":
        shift_start = datetime.fromisoformat(tool_input["shift_start"].replace("Z", "+00:00"))
        shift_end = datetime.fromisoformat(tool_input["shift_end"].replace("Z", "+00:00"))
        incidents = get_incidents(shift_start, shift_end)
        return _format_incidents(incidents)

    elif tool_name == "get_ongoing_incidents":
        incidents = get_ongoing_incidents()
        return _format_incidents(incidents)

    elif tool_name == "get_deployments":
        shift_start = datetime.fromisoformat(tool_input["shift_start"].replace("Z", "+00:00"))
        shift_end = datetime.fromisoformat(tool_input["shift_end"].replace("Z", "+00:00"))
        deployments = get_deployments(shift_start, shift_end)
        return _format_deployments(deployments)

    elif tool_name == "get_open_tickets":
        tickets = get_open_tickets()
        return _format_tickets(tickets)

    elif tool_name == "get_high_priority_tickets":
        tickets = get_high_priority_tickets()
        return _format_tickets(tickets)

    elif tool_name == "get_slack_threads":
        since = datetime.fromisoformat(tool_input["since"].replace("Z", "+00:00"))
        threads = slack_client.get_threads_since(tool_input["channel"], since)
        return _format_threads(threads)

    else:
        return f"Unknown tool: {tool_name}"


def _format_incidents(incidents) -> str:
    if not incidents:
        return "No incidents found."

    lines = ["Incidents:"]
    for inc in incidents:
        resolved = f", resolved: {inc.resolved_at.isoformat()}" if inc.resolved_at else ""
        lines.append(
            f"- [{inc.id}] {inc.title} | severity: {inc.severity.value} | "
            f"status: {inc.status.value} | service: {inc.service} | "
            f"assigned: {inc.assigned_to or 'unassigned'}{resolved}"
        )
        lines.append(f"  Summary: {inc.summary}")
    return "\n".join(lines)


def _format_deployments(deployments) -> str:
    if not deployments:
        return "No deployments found."

    lines = ["Deployments:"]
    for dep in deployments:
        lines.append(
            f"- [{dep.id}] {dep.service} {dep.version} | status: {dep.status.value} | "
            f"by: {dep.deployed_by} | at: {dep.deployed_at.isoformat()}"
        )
        if dep.changelog:
            lines.append(f"  Changelog: {dep.changelog}")
    return "\n".join(lines)


def _format_tickets(tickets) -> str:
    if not tickets:
        return "No tickets found."

    lines = ["Tickets:"]
    for t in tickets:
        lines.append(
            f"- [{t.id}] {t.title} | priority: {t.priority.value} | "
            f"status: {t.status.value} | assignee: {t.assignee or 'unassigned'}"
        )
    return "\n".join(lines)


def _format_threads(threads) -> str:
    if not threads:
        return "No relevant Slack threads found."

    lines = ["Slack Threads:"]
    for t in threads:
        lines.append(
            f"- {t.channel} ({t.message_count} messages) | participants: {', '.join(t.participants)}"
        )
        lines.append(f"  Link: {t.permalink}")
        if t.summary:
            lines.append(f"  Summary: {t.summary}")
    return "\n".join(lines)

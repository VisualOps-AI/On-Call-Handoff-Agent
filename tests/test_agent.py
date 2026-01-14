import pytest
from src.agent.tools import execute_tool, TOOL_DEFINITIONS
from src.agent.prompts import SYSTEM_PROMPT, get_handoff_prompt


class TestTools:
    def test_tool_definitions_valid(self):
        assert len(TOOL_DEFINITIONS) > 0

        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_execute_get_incidents(self):
        result = execute_tool(
            "get_incidents",
            {
                "shift_start": "2026-01-14T00:00:00Z",
                "shift_end": "2026-01-14T23:59:59Z",
            },
        )

        assert isinstance(result, str)
        assert "Incidents:" in result or "No incidents found" in result

    def test_execute_get_ongoing_incidents(self):
        result = execute_tool("get_ongoing_incidents", {})

        assert isinstance(result, str)

    def test_execute_get_deployments(self):
        result = execute_tool(
            "get_deployments",
            {
                "shift_start": "2026-01-14T00:00:00Z",
                "shift_end": "2026-01-14T23:59:59Z",
            },
        )

        assert isinstance(result, str)
        assert "Deployments:" in result or "No deployments found" in result

    def test_execute_get_open_tickets(self):
        result = execute_tool("get_open_tickets", {})

        assert isinstance(result, str)

    def test_execute_unknown_tool(self):
        result = execute_tool("unknown_tool", {})

        assert "Unknown tool" in result


class TestPrompts:
    def test_system_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT) > 0
        assert "On-Call Handoff" in SYSTEM_PROMPT

    def test_get_handoff_prompt(self):
        prompt = get_handoff_prompt(
            shift_start="2026-01-14T09:00:00Z",
            shift_end="2026-01-14T17:00:00Z",
            outgoing="alice",
            incoming="bob",
        )

        assert "2026-01-14T09:00:00Z" in prompt
        assert "2026-01-14T17:00:00Z" in prompt
        assert "alice" in prompt
        assert "bob" in prompt

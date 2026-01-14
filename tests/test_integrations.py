import pytest
from datetime import datetime, timezone
from src.integrations.incidents import get_incidents, get_ongoing_incidents
from src.integrations.deployments import get_deployments
from src.integrations.tickets import get_open_tickets, get_high_priority_tickets


class TestIncidents:
    def test_get_incidents_returns_list(self):
        shift_start = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)
        shift_end = datetime(2026, 1, 14, 23, 59, tzinfo=timezone.utc)

        incidents = get_incidents(shift_start, shift_end)

        assert isinstance(incidents, list)
        assert len(incidents) > 0

    def test_get_ongoing_incidents(self):
        ongoing = get_ongoing_incidents()

        assert isinstance(ongoing, list)
        for inc in ongoing:
            assert inc.status.value != "resolved"


class TestDeployments:
    def test_get_deployments_returns_list(self):
        shift_start = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)
        shift_end = datetime(2026, 1, 14, 23, 59, tzinfo=timezone.utc)

        deployments = get_deployments(shift_start, shift_end)

        assert isinstance(deployments, list)
        assert len(deployments) > 0

    def test_deployments_have_required_fields(self):
        shift_start = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)
        shift_end = datetime(2026, 1, 14, 23, 59, tzinfo=timezone.utc)

        deployments = get_deployments(shift_start, shift_end)

        for dep in deployments:
            assert dep.id
            assert dep.service
            assert dep.version
            assert dep.deployed_by


class TestTickets:
    def test_get_open_tickets(self):
        tickets = get_open_tickets()

        assert isinstance(tickets, list)
        for ticket in tickets:
            assert ticket.status.value not in ("resolved", "closed")

    def test_get_high_priority_tickets(self):
        tickets = get_high_priority_tickets()

        assert isinstance(tickets, list)
        for ticket in tickets:
            assert ticket.priority.value in ("urgent", "high")

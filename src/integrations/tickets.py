import json
from src.config import MOCK_DATA_DIR
from src.models.schemas import Ticket


def get_open_tickets() -> list[Ticket]:
    with open(MOCK_DATA_DIR / "tickets.json") as f:
        raw_tickets = json.load(f)

    tickets = [Ticket(**t) for t in raw_tickets]
    return [t for t in tickets if t.status not in ("resolved", "closed")]


def get_high_priority_tickets() -> list[Ticket]:
    open_tickets = get_open_tickets()
    return [t for t in open_tickets if t.priority in ("urgent", "high")]

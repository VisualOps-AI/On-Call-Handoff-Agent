import json
from datetime import datetime
from src.config import MOCK_DATA_DIR
from src.models.schemas import Incident


def get_incidents(shift_start: datetime, shift_end: datetime) -> list[Incident]:
    with open(MOCK_DATA_DIR / "incidents.json") as f:
        raw_incidents = json.load(f)

    incidents = [Incident(**inc) for inc in raw_incidents]

    return [
        inc
        for inc in incidents
        if shift_start <= inc.created_at <= shift_end
        or (inc.resolved_at and shift_start <= inc.resolved_at <= shift_end)
        or (inc.status != "resolved" and inc.created_at <= shift_end)
    ]


def get_ongoing_incidents() -> list[Incident]:
    with open(MOCK_DATA_DIR / "incidents.json") as f:
        raw_incidents = json.load(f)

    incidents = [Incident(**inc) for inc in raw_incidents]
    return [inc for inc in incidents if inc.status != "resolved"]

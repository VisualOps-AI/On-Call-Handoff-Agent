import json
from datetime import datetime
from src.config import MOCK_DATA_DIR
from src.models.schemas import Deployment


def get_deployments(shift_start: datetime, shift_end: datetime) -> list[Deployment]:
    with open(MOCK_DATA_DIR / "deployments.json") as f:
        raw_deployments = json.load(f)

    deployments = [Deployment(**dep) for dep in raw_deployments]

    return [
        dep for dep in deployments if shift_start <= dep.deployed_at <= shift_end
    ]

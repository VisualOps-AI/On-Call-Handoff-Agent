from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class DeploymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    IN_PROGRESS = "in_progress"


class TicketPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(BaseModel):
    id: str
    title: str
    severity: Severity
    status: IncidentStatus
    created_at: datetime
    resolved_at: datetime | None = None
    summary: str
    service: str
    assigned_to: str | None = None
    slack_thread_url: str | None = None


class Deployment(BaseModel):
    id: str
    service: str
    version: str
    previous_version: str | None = None
    deployed_by: str
    deployed_at: datetime
    status: DeploymentStatus
    commit_sha: str | None = None
    changelog: str | None = None


class Ticket(BaseModel):
    id: str
    title: str
    status: TicketStatus
    priority: TicketPriority
    assignee: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    labels: list[str] = Field(default_factory=list)


class SlackThread(BaseModel):
    channel: str
    thread_ts: str
    permalink: str
    message_count: int
    participants: list[str]
    summary: str | None = None


class ShiftSummary(BaseModel):
    total_incidents: int
    resolved_incidents: int
    ongoing_incidents: int
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    high_priority_tickets: int


class ActionItem(BaseModel):
    description: str
    priority: str
    related_incident_id: str | None = None


class HandoffBrief(BaseModel):
    shift_start: datetime
    shift_end: datetime
    outgoing_engineer: str | None = None
    incoming_engineer: str | None = None
    summary: ShiftSummary
    ongoing_issues: list[Incident]
    incidents: list[Incident]
    deployments: list[Deployment]
    open_tickets: list[Ticket]
    key_slack_threads: list[SlackThread]
    action_items: list[ActionItem]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

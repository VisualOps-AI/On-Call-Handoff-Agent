# On-Call Handoff Agent

An AI-powered agent that generates comprehensive shift handoff briefs for on-call engineers. Aggregates incidents, deployments, tickets, and Slack discussions to create actionable handoff documents.

## Problem

On-call handoffs are often:
- Incomplete (engineers forget to mention ongoing issues)
- Time-consuming (manually checking multiple systems)
- Inconsistent (different formats, missing context)

This agent automates the entire process, ensuring incoming engineers have full context.

## Features

- **Multi-source aggregation**: Pulls data from incident management, deployments, tickets, and Slack
- **AI-powered summarization**: Uses Claude to analyze and correlate information
- **Multiple triggers**: CLI, Slack `/handoff` command, or scheduled automation
- **Structured output**: Consistent markdown format with actionable sections

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     TRIGGERS                            │
│   CLI Command  │  Slack /handoff  │  Scheduler (cron)  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              HANDOFF AGENT (Claude)                     │
│  • Orchestrates data collection via tools               │
│  • Analyzes and correlates information                  │
│  • Generates structured handoff brief                   │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
   Incidents      Slack        Deployments    Tickets
     Tool          Tool           Tool          Tool
```

## Quick Start

### 1. Install dependencies

```bash
cd on-call-handoff-agent
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

Optional (for Slack integration):
- `SLACK_BOT_TOKEN`: Slack bot token (xoxb-...)
- `SLACK_APP_TOKEN`: Slack app token (xapp-...)

### 3. Generate a handoff

```bash
# CLI usage
python main.py handoff --shift-hours 8

# With names
python main.py handoff -s 8 --outgoing alice --incoming bob

# Save to file
python main.py handoff -s 8 --output handoff.md

# Post to Slack
python main.py handoff -s 8 --slack
```

## Usage

### CLI Commands

```bash
# Generate handoff brief
python main.py handoff [OPTIONS]

Options:
  -s, --shift-hours INTEGER  Shift duration in hours [default: 8]
  -o, --outgoing TEXT        Outgoing engineer name
  -i, --incoming TEXT        Incoming engineer name
  -f, --output TEXT          Save to file
  --slack                    Post to Slack channel

# Validate configuration
python main.py cli validate

# Run Slack bot
python main.py slack

# Run scheduler
python main.py schedule --hours "9,17"
```

### Slack Integration

1. Create a Slack app at api.slack.com
2. Enable Socket Mode
3. Add the `/handoff` slash command
4. Install to workspace and get tokens
5. Run: `python main.py slack`

Usage in Slack:
```
/handoff
/handoff 8h
/handoff 8h from @alice to @bob
```

### Scheduled Handoffs

Automatically post handoffs at shift boundaries:

```bash
# Default: 9am and 5pm UTC
python main.py schedule

# Custom hours
python main.py schedule --hours "6,14,22"
```

## Example Output

```markdown
# On-Call Handoff Brief
**Shift:** 2026-01-14 09:00 - 17:00 UTC
**Outgoing:** @alice | **Incoming:** @bob

## Shift Summary
- **Incidents:** 3 triggered, 2 resolved, 1 ongoing
- **Deployments:** 5 successful, 0 failed
- **Open Tickets:** 2 high priority

## Ongoing Issues

### [INC-1234] Database connection timeouts
- **Status:** Investigating
- **Severity:** High
- **Service:** api-gateway
- **Summary:** Intermittent connection timeouts to primary DB.
  Increased pool size from 20 to 50, monitoring metrics.
- **Action:** Monitor DB connections, escalate if timeouts persist after 18:00

## Incidents This Shift

| ID | Title | Severity | Status | Duration |
|----|-------|----------|--------|----------|
| INC-1234 | DB connection timeouts | High | Investigating | 2h 15m |
| INC-1235 | API latency spike | Medium | Resolved | 45m |
| INC-1236 | Login failures | Low | Resolved | 20m |

## Deployments

| Service | Version | Status | Deployed By | Notes |
|---------|---------|--------|-------------|-------|
| auth-service | v2.3.1 | Success | carol | OAuth hotfix |
| api-gateway | v1.8.0 | Success | dave | Connection pool increase |

## Action Items for Incoming

1. **Monitor DB metrics** - Alert threshold lowered, watch for timeouts
2. **Follow up on INC-1234** - Escalate if not resolved by 18:00
3. **Review PR #456** - auth-service hotfix pending approval

## Key Slack Threads

- [#incidents: DB timeout discussion](https://slack.com/...) - 12 messages
- [#deployments: API gateway rollout](https://slack.com/...) - 5 messages
```

## Project Structure

```
on-call-handoff-agent/
├── src/
│   ├── agent/
│   │   ├── handoff_agent.py   # Main agent orchestration
│   │   ├── tools.py           # Tool definitions for Claude
│   │   └── prompts.py         # System prompts
│   ├── integrations/
│   │   ├── incidents.py       # Incident data fetching
│   │   ├── deployments.py     # Deployment data fetching
│   │   ├── tickets.py         # Ticket data fetching
│   │   └── slack_client.py    # Slack API wrapper
│   ├── models/
│   │   └── schemas.py         # Pydantic data models
│   ├── triggers/
│   │   ├── cli.py             # CLI interface
│   │   ├── slack_bot.py       # Slack bot handler
│   │   └── scheduler.py       # Cron scheduler
│   └── config.py              # Configuration management
├── tests/
├── mock_data/                 # Sample data for development
├── main.py                    # Entry point
└── requirements.txt
```

## Extending

### Adding Real Integrations

The mock integrations can be replaced with real APIs:

```python
# src/integrations/incidents.py
# Replace mock data loading with PagerDuty/OpsGenie API calls

from pagerduty import PagerDutyClient

def get_incidents(shift_start, shift_end):
    client = PagerDutyClient(api_key=config.PAGERDUTY_API_KEY)
    return client.incidents.list(since=shift_start, until=shift_end)
```

### Adding New Tools

Add tools in `src/agent/tools.py`:

```python
TOOL_DEFINITIONS.append({
    "name": "get_runbook",
    "description": "Fetch runbook for a specific service",
    "input_schema": {...}
})
```

## Testing

```bash
pytest tests/ -v
```

## Tech Stack

- **Python 3.11+**
- **Anthropic Claude** - AI orchestration
- **Pydantic** - Data validation
- **Typer** - CLI framework
- **slack-sdk** - Slack integration
- **APScheduler** - Task scheduling

## License

MIT

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.config import config
from src.agent.handoff_agent import create_agent
from src.integrations.slack_client import slack_client


def generate_and_post_handoff():
    print(f"[{datetime.utcnow().isoformat()}] Running scheduled handoff...")

    try:
        agent = create_agent()
        brief = agent.generate_handoff(shift_hours=config.SHIFT_DURATION_HOURS)

        success = slack_client.post_message(config.HANDOFF_CHANNEL, brief)
        if success:
            print("Handoff posted to Slack successfully")
        else:
            print("Failed to post handoff to Slack")

    except Exception as e:
        print(f"Error generating scheduled handoff: {e}")


def run_scheduler(shift_end_hours: list[int] | None = None):
    """
    Run the scheduler to automatically generate handoffs at shift boundaries.

    Args:
        shift_end_hours: List of hours (UTC) when shifts end.
                        Default: [9, 17] for 9am and 5pm UTC
    """
    if shift_end_hours is None:
        shift_end_hours = [9, 17]

    scheduler = BlockingScheduler()

    for hour in shift_end_hours:
        trigger = CronTrigger(hour=hour, minute=0, timezone="UTC")
        scheduler.add_job(
            generate_and_post_handoff,
            trigger=trigger,
            id=f"handoff_{hour}",
            name=f"Handoff at {hour}:00 UTC",
        )
        print(f"Scheduled handoff at {hour}:00 UTC")

    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Scheduler stopped.")

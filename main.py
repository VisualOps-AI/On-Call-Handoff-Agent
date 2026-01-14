import sys
import typer
from src.triggers.cli import app as cli_app
from src.triggers.slack_bot import run_slack_bot
from src.triggers.scheduler import run_scheduler

main_app = typer.Typer(help="On-Call Handoff Agent")

main_app.add_typer(cli_app, name="cli", help="CLI commands for generating handoffs")


@main_app.command()
def slack():
    """Run the Slack bot to handle /handoff commands."""
    run_slack_bot()


@main_app.command()
def schedule(
    hours: str = typer.Option(
        "9,17",
        "--hours",
        "-h",
        help="Comma-separated list of hours (UTC) when handoffs should run",
    )
):
    """Run the scheduler for automatic handoffs at shift boundaries."""
    shift_hours = [int(h.strip()) for h in hours.split(",")]
    run_scheduler(shift_hours)


@main_app.command()
def handoff(
    shift_hours: int = typer.Option(8, "--shift-hours", "-s"),
    outgoing: str = typer.Option(None, "--outgoing", "-o"),
    incoming: str = typer.Option(None, "--incoming", "-i"),
    output: str = typer.Option(None, "--output", "-f"),
    post_slack: bool = typer.Option(False, "--slack"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show agent tool calls"),
):
    """Generate a handoff brief (shortcut for cli handoff)."""
    from src.triggers.cli import handoff as cli_handoff
    cli_handoff(
        shift_hours=shift_hours,
        outgoing=outgoing,
        incoming=incoming,
        output=output,
        post_slack=post_slack,
        verbose=verbose,
    )


if __name__ == "__main__":
    main_app()

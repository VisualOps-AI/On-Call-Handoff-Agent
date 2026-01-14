from datetime import datetime
from pathlib import Path
import sys
import typer
from rich.console import Console
from rich.markdown import Markdown
from src.agent.handoff_agent import create_agent
from src.integrations.slack_client import slack_client
from src.config import config

app = typer.Typer(help="On-Call Handoff Agent CLI")

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)


@app.command()
def handoff(
    shift_hours: int = typer.Option(
        8, "--shift-hours", "-s", help="Duration of the shift in hours"
    ),
    outgoing: str = typer.Option(
        None, "--outgoing", "-o", help="Outgoing engineer's name"
    ),
    incoming: str = typer.Option(
        None, "--incoming", "-i", help="Incoming engineer's name"
    ),
    output: str = typer.Option(
        None, "--output", "-f", help="Save output to file (markdown)"
    ),
    post_slack: bool = typer.Option(
        False, "--slack", help="Post handoff brief to Slack"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show agent tool calls in real-time"
    ),
):
    """Generate an on-call handoff brief for the current shift."""
    console.print("[bold blue]Generating handoff brief...[/bold blue]")

    try:
        agent = create_agent()
        brief = agent.generate_handoff(
            shift_hours=shift_hours,
            outgoing=outgoing,
            incoming=incoming,
            verbose=verbose,
        )

        console.print("\n")
        console.print(Markdown(brief))

        if output:
            output_path = Path(output)
            output_path.write_text(brief, encoding="utf-8")
            console.print(f"\n[green]Saved to {output_path}[/green]")

        if post_slack:
            success = slack_client.post_message(config.HANDOFF_CHANNEL, brief)
            if success:
                console.print(
                    f"\n[green]Posted to {config.HANDOFF_CHANNEL}[/green]"
                )
            else:
                console.print("\n[red]Failed to post to Slack[/red]")

    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error generating handoff: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate():
    """Validate configuration and connectivity."""
    console.print("[bold]Checking configuration...[/bold]\n")

    errors = config.validate()
    if errors:
        for err in errors:
            console.print(f"[red]✗ {err}[/red]")
    else:
        console.print("[green]✓ Anthropic API key configured[/green]")

    if config.SLACK_BOT_TOKEN:
        console.print("[green]✓ Slack bot token configured[/green]")
    else:
        console.print("[yellow]⚠ Slack bot token not configured (mock mode)[/yellow]")

    console.print(f"\n[dim]Shift duration: {config.SHIFT_DURATION_HOURS} hours[/dim]")
    console.print(f"[dim]Handoff channel: {config.HANDOFF_CHANNEL}[/dim]")


if __name__ == "__main__":
    app()

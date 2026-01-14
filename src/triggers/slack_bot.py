import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import config
from src.agent.handoff_agent import create_agent


def create_slack_app() -> App | None:
    if not config.SLACK_BOT_TOKEN or not config.SLACK_APP_TOKEN:
        return None

    app = App(token=config.SLACK_BOT_TOKEN)

    @app.command("/handoff")
    def handle_handoff_command(ack, respond, command):
        ack()
        respond("Generating handoff brief... This may take a moment.")

        try:
            text = command.get("text", "")
            shift_hours = config.SHIFT_DURATION_HOURS
            outgoing = None
            incoming = None

            hours_match = re.search(r"(\d+)\s*h(?:ours?)?", text)
            if hours_match:
                shift_hours = int(hours_match.group(1))

            outgoing_match = re.search(r"from\s+@?(\w+)", text)
            if outgoing_match:
                outgoing = outgoing_match.group(1)

            incoming_match = re.search(r"to\s+@?(\w+)", text)
            if incoming_match:
                incoming = incoming_match.group(1)

            agent = create_agent()
            brief = agent.generate_handoff(
                shift_hours=shift_hours,
                outgoing=outgoing,
                incoming=incoming,
            )

            respond(brief)

        except Exception as e:
            respond(f"Error generating handoff: {str(e)}")

    @app.event("app_mention")
    def handle_mention(event, say):
        text = event.get("text", "").lower()
        if "handoff" in text:
            say("Use `/handoff` to generate a handoff brief. Options: `/handoff 8h from @alice to @bob`")
        else:
            say("I can help with on-call handoffs. Use `/handoff` to generate a brief.")

    return app


def run_slack_bot():
    app = create_slack_app()
    if app is None:
        print("Slack bot not configured. Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN.")
        return

    handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)
    print("Starting Slack bot...")
    handler.start()

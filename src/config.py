import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
MOCK_DATA_DIR = BASE_DIR / "mock_data"


class Config:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
    HANDOFF_CHANNEL: str = os.getenv("HANDOFF_CHANNEL", "#oncall-handoff")

    SHIFT_DURATION_HOURS: int = int(os.getenv("SHIFT_DURATION_HOURS", "8"))
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")
        return errors


config = Config()

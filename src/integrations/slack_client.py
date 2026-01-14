from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.config import config
from src.models.schemas import SlackThread


class SlackClient:
    def __init__(self):
        self.client = WebClient(token=config.SLACK_BOT_TOKEN) if config.SLACK_BOT_TOKEN else None

    def _is_configured(self) -> bool:
        return self.client is not None and bool(config.SLACK_BOT_TOKEN)

    def get_threads_since(
        self, channel: str, since: datetime, limit: int = 10
    ) -> list[SlackThread]:
        if not self._is_configured():
            return self._get_mock_threads()

        try:
            result = self.client.conversations_history(
                channel=channel,
                oldest=str(since.timestamp()),
                limit=100,
            )

            threads = []
            for msg in result.get("messages", []):
                if msg.get("reply_count", 0) > 0:
                    permalink_resp = self.client.chat_getPermalink(
                        channel=channel, message_ts=msg["ts"]
                    )

                    replies = self.client.conversations_replies(
                        channel=channel, ts=msg["ts"]
                    )
                    participants = list(
                        {r.get("user", "unknown") for r in replies.get("messages", [])}
                    )

                    threads.append(
                        SlackThread(
                            channel=channel,
                            thread_ts=msg["ts"],
                            permalink=permalink_resp.get("permalink", ""),
                            message_count=msg.get("reply_count", 0),
                            participants=participants,
                            summary=msg.get("text", "")[:200],
                        )
                    )

                    if len(threads) >= limit:
                        break

            return threads

        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")
            return []

    def _get_mock_threads(self) -> list[SlackThread]:
        return [
            SlackThread(
                channel="#incidents",
                thread_ts="1705234567.123456",
                permalink="https://slack.com/archives/C123/p1705234567",
                message_count=12,
                participants=["alice", "bob", "carol"],
                summary="DB timeout investigation - increased pool size, monitoring",
            ),
            SlackThread(
                channel="#deployments",
                thread_ts="1705231234.654321",
                permalink="https://slack.com/archives/C456/p1705231234",
                message_count=5,
                participants=["dave", "eve"],
                summary="API gateway v1.8.0 rollout complete",
            ),
        ]

    def post_message(self, channel: str, text: str, blocks: list | None = None) -> bool:
        if not self._is_configured():
            print(f"[Mock] Would post to {channel}:\n{text}")
            return True

        try:
            self.client.chat_postMessage(channel=channel, text=text, blocks=blocks)
            return True
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")
            return False


slack_client = SlackClient()

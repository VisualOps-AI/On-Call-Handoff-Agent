from datetime import datetime, timedelta
import httpx
import anthropic
from src.config import config
from src.agent.tools import TOOL_DEFINITIONS, execute_tool
from src.agent.prompts import SYSTEM_PROMPT, get_handoff_prompt


class HandoffAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=config.ANTHROPIC_API_KEY,
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
        self.model = config.ANTHROPIC_MODEL

    def generate_handoff(
        self,
        shift_hours: int = 8,
        shift_end: datetime | None = None,
        outgoing: str | None = None,
        incoming: str | None = None,
        verbose: bool = False,
    ) -> str:
        if shift_end is None:
            shift_end = datetime.utcnow()
        shift_start = shift_end - timedelta(hours=shift_hours)

        user_prompt = get_handoff_prompt(
            shift_start=shift_start.isoformat() + "Z",
            shift_end=shift_end.isoformat() + "Z",
            outgoing=outgoing,
            incoming=incoming,
        )

        messages = [{"role": "user", "content": user_prompt}]

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                return self._extract_text(response)

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        if verbose:
                            print(f"\n{'='*50}")
                            print(f"TOOL CALL: {block.name}")
                            print(f"INPUT: {block.input}")
                            print(f"{'='*50}")

                        result = execute_tool(block.name, block.input)

                        if verbose:
                            preview = result[:200] + "..." if len(result) > 200 else result
                            print(f"RESULT: {preview}")

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )

                messages.append({"role": "user", "content": tool_results})
            else:
                return self._extract_text(response)

    def _extract_text(self, response) -> str:
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]
        return "\n".join(text_blocks)


def create_agent() -> HandoffAgent:
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    return HandoffAgent()

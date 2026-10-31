"""Keep a conversation's history within what one model call can take."""

import json
from typing import Any

# About 75k tokens of history at roughly four characters a token, leaving room in the
# context window for the system prompt, tool definitions, and the reply.
DEFAULT_HISTORY_CHARS = 300_000


def _is_question(message: dict[str, Any]) -> bool:
    """A user turn of plain text, as opposed to one carrying tool results."""
    return message.get("role") == "user" and isinstance(message.get("content"), str)


def window_messages(
    messages: list[dict[str, Any]],
    max_chars: int = DEFAULT_HISTORY_CHARS,
) -> list[dict[str, Any]]:
    """The newest part of ``messages`` that fits in ``max_chars``, starting on a question.

    A conversation that grows without bound eventually exceeds the model's context
    window, and every call after that is refused. This keeps the most recent turns
    whose serialized size fits the budget, then moves the start forward to the first
    plain-text user turn, so the window never opens on a ``tool_result`` whose
    ``tool_use`` was cut off. The latest question is always kept, even when it alone
    exceeds the budget.

    Pass the result to ``messages.create``. A stored history can be trimmed the same
    way, with a larger budget.
    """
    start = len(messages)
    used = 0
    while start > 0:
        size = len(json.dumps(messages[start - 1], default=str))
        if used + size > max_chars:
            break
        used = used + size
        start = start - 1

    for index in range(start, len(messages)):
        if _is_question(messages[index]):
            return messages[index:]

    for index in range(len(messages) - 1, -1, -1):
        if _is_question(messages[index]):
            return messages[index:]
    return messages[start:]


__exports__ = ("DEFAULT_HISTORY_CHARS", "window_messages")

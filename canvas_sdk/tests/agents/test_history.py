import json
from typing import Any

from canvas_sdk.agents import window_messages


def _question(text: str) -> dict[str, Any]:
    return {"role": "user", "content": text}


def _tool_call(tool_id: str) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": [{"type": "tool_use", "id": tool_id, "name": "find_vitals", "input": {}}],
    }


def _tool_result(tool_id: str, size: int) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": "x" * size}],
    }


def _answer(text: str) -> dict[str, Any]:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def _size(messages: list[dict[str, Any]]) -> int:
    return sum(len(json.dumps(message)) for message in messages)


def test_history_within_budget_is_unchanged() -> None:
    """A short conversation goes to the model whole."""
    messages = [_question("q1"), _answer("a1"), _question("q2")]
    assert window_messages(messages, max_chars=10_000) == messages


def test_history_over_budget_keeps_the_newest_turns() -> None:
    """Older turns drop off once the history outgrows the budget."""
    old = [_question("q1"), _tool_call("t1"), _tool_result("t1", 5_000), _answer("a1")]
    recent = [_question("q2"), _answer("a2"), _question("q3")]

    windowed = window_messages(old + recent, max_chars=_size(recent) + 100)

    assert windowed == recent


def test_window_never_starts_on_a_tool_result() -> None:
    """A tool_result without its tool_use is rejected by the API, so the window starts on a question."""
    messages = [
        _question("q1"),
        _tool_call("t1"),
        _tool_result("t1", 2_000),
        _answer("a1"),
        _question("q2"),
        _tool_call("t2"),
        _tool_result("t2", 50),
        _answer("a2"),
    ]
    budget = _size(messages[2:])  # would start on t1's tool_result

    windowed = window_messages(messages, max_chars=budget)

    assert windowed == messages[4:]
    assert windowed[0]["content"] == "q2"


def test_window_keeps_the_latest_question_even_over_budget() -> None:
    """The turn being answered always reaches the model."""
    messages = [_question("q1"), _answer("a1"), _question("q2" + "y" * 500)]

    assert window_messages(messages, max_chars=10) == messages[2:]

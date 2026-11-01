from typing import Any

from agent_runner_poc.agents.chart_chat import SYSTEM_PROMPT as CHART_PROMPT
from agent_runner_poc.agents.chart_chat_tools import tools as chart_chat_tools
from agent_runner_poc.agents.claims_chat import SYSTEM_PROMPT as CLAIMS_PROMPT
from agent_runner_poc.agents.suggestions import split_suggestions
from agent_runner_poc.applications.chart_chat import _ui_messages

REPLY = (
    "Her A1c rose from 6.8 to 7.4 over the year.\n\n"
    "```suggestions\n"
    '["Trend her A1c over 12 months", "Show the last visit note"]\n'
    "```"
)


def test_a_replys_suggestions_come_out_of_its_text() -> None:
    """The clinician sees the answer, and the prompts as chips."""
    text, chips = split_suggestions(REPLY)

    assert text == "Her A1c rose from 6.8 to 7.4 over the year."
    assert chips == ["Trend her A1c over 12 months", "Show the last visit note"]


def test_a_reply_without_suggestions_is_unchanged() -> None:
    """Most replies carry no block."""
    assert split_suggestions("No allergies on file.") == ("No allergies on file.", [])


def test_a_malformed_block_is_removed_and_offers_nothing() -> None:
    """A block that is not a JSON array of strings never shows as text or as chips."""
    for body in ('["unclosed"', '{"chips": ["a"]}', '"just a string"'):
        assert split_suggestions(f"Answer.\n```suggestions\n{body}\n```") == ("Answer.", [])


def test_suggestions_are_capped_in_number_and_length() -> None:
    """At most three chips, each short; blanks and non-strings are dropped."""
    block = '["  one  ", "", 7, "two", "three", "four", "' + "x" * 200 + '"]'

    _, chips = split_suggestions(f"Answer.\n```suggestions\n{block}\n```")

    assert chips == ["one", "two", "three"]
    _, (long_chip,) = split_suggestions(f'A.\n```suggestions\n["{"x" * 200}"]\n```')
    assert len(long_chip) == 80


def test_the_history_carries_each_replys_chips() -> None:
    """The chat draws the latest reply's chips; the stored reply keeps its block."""
    stored: list[dict[str, Any]] = [
        {"role": "user", "content": "How is her A1c?"},
        {"role": "assistant", "content": [{"type": "text", "text": REPLY}]},
    ]

    assert _ui_messages(stored, chart_chat_tools) == [
        {"role": "user", "text": "How is her A1c?"},
        {
            "role": "assistant",
            "text": "Her A1c rose from 6.8 to 7.4 over the year.",
            "chips": ["Trend her A1c over 12 months", "Show the last visit note"],
            "citations": [],
        },
    ]
    assert "```suggestions" in stored[1]["content"][0]["text"]


def test_both_chats_ask_for_suggestions_within_their_limits() -> None:
    """Chart chat never suggests a clinical choice; claims chat never suggests a code."""
    assert "```suggestions" in CHART_PROMPT
    assert "never a medication, dose, diagnosis, order, or other clinical choice" in CHART_PROMPT
    assert "```suggestions" in CLAIMS_PROMPT
    assert "never a code, a modifier, or a change to many claims at once" in CLAIMS_PROMPT

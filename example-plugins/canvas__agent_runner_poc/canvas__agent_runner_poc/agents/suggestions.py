"""Suggested next steps: short prompts a chat agent offers after a reply.

The agent ends a reply with a fenced block tagged ``suggestions`` holding a JSON array of
strings. The chat's history endpoint takes the block out of the reply's text with
:func:`split_suggestions` and returns the prompts as ``chips``, which the chat draws as
buttons that send the prompt as the user's next message. The stored conversation keeps
the block, so the model sees what it suggested.
"""

import json
import re

MAX_CHIPS = 3
MAX_CHIP_CHARS = 80

SUGGESTIONS_BLOCK = re.compile(r"```suggestions[ \t]*\n(.*?)```", re.DOTALL)


def suggestions_guidance(examples: str, scope: str) -> str:
    """The system prompt paragraph asking for suggestions, with the agent's own examples.

    ``examples`` is a JSON array of sample prompts; ``scope`` says what a suggestion may
    lead to in this agent's work.
    """
    return (
        "Suggested next steps: when an obvious follow-up exists, end your reply with "
        "2-3 short prompts the user could send next, as a fenced block tagged "
        "`suggestions` holding a JSON array of strings:\n"
        f"```suggestions\n{examples}\n```\n"
        f"Each at most 60 characters, phrased as the user would type it. {scope} "
        "No patient names. Leave the block out when the answer was trivial or nothing "
        "obvious follows. One block per reply, after your prose.\n\n"
    )


def split_suggestions(text: str) -> tuple[str, list[str]]:
    """Return ``text`` without its suggestions block, and the prompts the block held.

    A block that is not a JSON array of strings gives no prompts; it is removed all the
    same, so a malformed block never shows as text.
    """
    match = SUGGESTIONS_BLOCK.search(text)
    if match is None:
        return text, []
    stripped = SUGGESTIONS_BLOCK.sub("", text).strip()
    try:
        parsed = json.loads(match.group(1))
    except ValueError:
        return stripped, []
    if not isinstance(parsed, list):
        return stripped, []
    chips = [item.strip()[:MAX_CHIP_CHARS] for item in parsed if isinstance(item, str)]
    return stripped, [chip for chip in chips if chip][:MAX_CHIPS]

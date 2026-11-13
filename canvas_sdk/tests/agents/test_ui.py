import re

import pytest

from canvas_sdk.agents.ui import AGENT_UI_CSS, LATO_IMPORT, TOKENS


def _luminance(hex_color: str) -> float:
    def linear(channel: int) -> float:
        c = channel / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)


def _contrast(a: str, b: str) -> float:
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# (foreground, background, WCAG AA minimum): 4.5 for text, 3 for a control's outline.
PAIRS = [
    *[
        (fg, bg, 4.5)
        for fg in ("text", "text-secondary")
        for bg in ("bg", "bg-secondary", "bg-elevated", "bg-hover")
    ],
    *[
        (fg, bg, 4.5)
        for fg in ("good", "warning", "critical", "action")
        for bg in ("bg", "bg-elevated")
    ],
    ("agent", "bg", 4.5),
    ("agent", "agent-soft", 4.5),
    ("agent-fg", "agent", 4.5),
    ("action", "action-soft", 4.5),
    ("action-fg", "action", 4.5),
    ("warning", "warning-soft", 4.5),
    ("critical", "critical-soft", 4.5),
    ("input-border", "input-bg", 3),
    ("input-border", "bg", 3),
]


@pytest.mark.parametrize(("fg", "bg", "minimum"), PAIRS)
def test_color_pairs_clear_wcag_aa(fg: str, bg: str, minimum: float) -> None:
    """Every text and control color the stylesheet pairs clears WCAG AA."""
    ratio = _contrast(TOKENS[fg], TOKENS[bg])
    assert ratio >= minimum, f"{fg} on {bg} is {ratio:.2f}:1, below {minimum}:1"


@pytest.mark.parametrize(
    ("soft", "base", "percent"),
    [
        ("agent-soft", "agent", 12),
        ("action-soft", "action", 10),
        ("warning-soft", "warning", 10),
        ("critical-soft", "critical", 10),
    ],
)
def test_soft_tints_are_their_base_over_white(soft: str, base: str, percent: int) -> None:
    """A tint is its base color mixed over white, so it moves when the base does."""
    base_rgb = [int(TOKENS[base][i : i + 2], 16) for i in (1, 3, 5)]
    expected = "#" + "".join(f"{round(255 - (255 - c) * percent / 100):02x}" for c in base_rgb)
    assert TOKENS[soft] == expected


def test_stylesheet_uses_only_tokens_it_defines() -> None:
    """A var(--adk-*) with no token would fall back to the browser default unnoticed."""
    used = set(re.findall(r"var\(--adk-([a-z-]+)", AGENT_UI_CSS)) - {"author"}
    assert used <= set(TOKENS), f"undefined tokens: {sorted(used - set(TOKENS))}"
    for name, value in TOKENS.items():
        assert f"--adk-{name}: {value};" in AGENT_UI_CSS


def test_stylesheet_loads_the_charts_lato_first() -> None:
    """An @import after any rule is ignored, so the chart's font must lead."""
    assert AGENT_UI_CSS.startswith(f"@import url({LATO_IMPORT});")
    assert TOKENS["font"].startswith("Lato,")


AGENT_SELECTORS = (
    "adk-msg-agent",
    "adk-cite",
    "adk-record[aria-current",
    "adk-thinking-dot",
    "adk-running",
    "adk-note-agent",
)


def test_agent_purple_marks_only_what_the_agent_made() -> None:
    """Purple means the agent made it; a button or link in purple would blur that."""
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", AGENT_UI_CSS):
        if re.search(r"var\(--adk-agent(?:-soft|-fg)?\)", body):
            parts = [part.strip() for part in selector.split(",")]
            for part in parts:
                assert any(mark in part for mark in AGENT_SELECTORS), f"purple on {part!r}"


def test_tokens_cannot_be_changed_by_a_plugin() -> None:
    """Plugins share one process, so a plugin changing a token would restyle the rest."""
    with pytest.raises(TypeError):
        TOKENS["agent"] = "#000000"  # type: ignore[index]

import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.command_custom_html import _CommandCustomHtml


def test_apply_emits_effect_with_correct_type() -> None:
    """Calling .apply() produces a SET_COMMAND_CUSTOM_HTML effect."""
    effect = _CommandCustomHtml(
        command_id="71d20b55-8696-4d04-a848-ce5e0180e00e",  # type: ignore[arg-type]
        custom_html="<p>hi</p>",
    ).apply()

    assert effect.type == EffectType.SET_COMMAND_CUSTOM_HTML


def test_apply_emits_effect_with_correct_payload() -> None:
    """The payload nests both fields inside data."""
    effect = _CommandCustomHtml(
        command_id="71d20b55-8696-4d04-a848-ce5e0180e00e",  # type: ignore[arg-type]
        custom_html="<p>hi</p>",
    ).apply()

    assert json.loads(effect.payload) == {
        "data": {"command_id": "71d20b55-8696-4d04-a848-ce5e0180e00e", "custom_html": "<p>hi</p>"},
    }


def test_apply_transmits_none_to_clear() -> None:
    """Explicit None is preserved in the payload so the server can clear the field."""
    effect = _CommandCustomHtml(
        command_id="71d20b55-8696-4d04-a848-ce5e0180e00e",  # type: ignore[arg-type]
        custom_html=None,
    ).apply()

    assert json.loads(effect.payload)["data"]["custom_html"] is None


def test_construction_requires_command_id() -> None:
    """command_id is a required Pydantic field."""
    with pytest.raises(ValueError, match="command_id"):
        _CommandCustomHtml(custom_html="<p>hi</p>")  # type: ignore[call-arg]


def test_construction_requires_custom_html() -> None:
    """custom_html is a required Pydantic field."""
    with pytest.raises(ValueError, match="custom_html"):
        _CommandCustomHtml(command_id="71d20b55-8696-4d04-a848-ce5e0180e00e")  # type: ignore

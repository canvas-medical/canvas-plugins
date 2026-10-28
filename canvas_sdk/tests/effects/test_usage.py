import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.usage import MAX_QUANTITY, RecordUsage


def test_apply_carries_the_unit_key_and_quantity() -> None:
    """The effect sends what home-app records, one unit unless told otherwise."""
    effect = RecordUsage(unit="visit", key="visit:abc").apply()

    assert effect.type == EffectType.RECORD_USAGE
    assert json.loads(effect.payload) == {
        "data": {"unit": "visit", "key": "visit:abc", "quantity": 1}
    }


def test_a_quantity_is_sent_as_given() -> None:
    """Several units of one kind of work go in one record."""
    effect = RecordUsage(unit="page", key="fax:1", quantity=12).apply()

    assert json.loads(effect.payload)["data"]["quantity"] == 12


@pytest.mark.parametrize(
    "fields",
    [
        {"unit": "", "key": "k"},
        {"unit": "u" * 41, "key": "k"},
        {"unit": "visit", "key": ""},
        {"unit": "visit", "key": "k" * 257},
        {"unit": "visit", "key": "k", "quantity": 0},
        {"unit": "visit", "key": "k", "quantity": -1},
        {"unit": "visit", "key": "k", "quantity": MAX_QUANTITY + 1},
        {"unit": "visit", "key": "k", "quantity": 1.5},
    ],
    ids=[
        "empty-unit",
        "long-unit",
        "empty-key",
        "long-key",
        "zero",
        "negative",
        "over-the-cap",
        "fraction",
    ],
)
def test_an_invalid_record_is_refused(fields: dict) -> None:
    """A record home-app could not store is refused in the plugin, where its author sees it."""
    with pytest.raises(ValidationError):
        RecordUsage(**fields).apply()

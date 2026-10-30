import json

import pytest

from canvas_generated.messages.effects_pb2 import Effect, EffectType
from plugin_runner.usage import permitted_usage, unit_name, usage_units


def _usage(
    unit: object,
    *,
    key: object = "visit:1",
    quantity: object = 1,
    async_props: dict | None = None,
) -> Effect:
    payload: dict = {"data": {"unit": unit, "key": key, "quantity": quantity}}
    if async_props is not None:
        payload["async_props"] = async_props
    return Effect(type=EffectType.RECORD_USAGE, payload=json.dumps(payload), plugin_name="acme")


def test_a_unit_is_matched_as_platform_matches_it() -> None:
    """Case and runs of whitespace do not distinguish two units."""
    assert unit_name("  Office   Visit ") == "office visit"


def test_the_units_are_the_manifest_pricing_without_token() -> None:
    """Tokens are priced by the inference gateway, so a plugin never records them."""
    manifest = {
        "catalog": {"pricing": [{"unit": "Visit", "price_per_unit": "1"}, {"unit": "Token"}]}
    }

    assert usage_units(manifest) == frozenset({"visit"})


@pytest.mark.parametrize(
    "manifest",
    [{}, {"catalog": None}, {"catalog": {}}, {"catalog": {"pricing": "visit"}}],
    ids=["no-catalog", "null-catalog", "no-pricing", "pricing-not-a-list"],
)
def test_a_manifest_without_pricing_has_no_units(manifest: dict) -> None:
    """An unpriced plugin may record nothing."""
    assert usage_units(manifest) == frozenset()


def test_a_priced_unit_is_kept_and_written_as_matched() -> None:
    """The unit reaches home-app in the form Platform matches on."""
    [kept] = permitted_usage([_usage(" VISIT ")], frozenset({"visit"}))

    assert json.loads(kept.payload)["data"]["unit"] == "visit"


@pytest.mark.parametrize(
    "effect",
    [
        _usage("minute"),
        _usage("token"),
        _usage(7),
        _usage("visit", key=""),
        _usage("visit", key="k" * 257),
        _usage("visit", key=1),
        _usage("visit", quantity=0),
        _usage("visit", quantity=10_001),
        _usage("visit", quantity=True),
        _usage("visit", quantity=1.0),
        _usage("visit", quantity="1"),
        _usage("visit", async_props={"delay_seconds": 0}),
        Effect(type=EffectType.RECORD_USAGE, payload="not json", plugin_name="acme"),
        Effect(type=EffectType.RECORD_USAGE, payload="{}", plugin_name="acme"),
    ],
    ids=[
        "unpriced",
        "token",
        "not-a-string",
        "empty-key",
        "long-key",
        "key-not-a-string",
        "zero",
        "over-the-cap",
        "bool-quantity",
        "float-quantity",
        "string-quantity",
        "async",
        "not-json",
        "no-data",
    ],
)
def test_usage_the_plugin_may_not_record_is_dropped(effect: Effect) -> None:
    """Only a well-formed record in a priced unit, applied with its response, goes on."""
    assert permitted_usage([effect], frozenset({"visit"})) == []


def test_a_kept_record_carries_only_its_unit_key_and_quantity() -> None:
    """Anything else a hand-built payload adds is left behind."""
    effect = Effect(
        type=EffectType.RECORD_USAGE,
        payload=json.dumps({"data": {"unit": "visit", "key": "k", "quantity": 2, "x": 1}, "y": 2}),
        plugin_name="acme",
    )

    [kept] = permitted_usage([effect], frozenset({"visit"}))

    assert json.loads(kept.payload) == {"data": {"unit": "visit", "key": "k", "quantity": 2}}


def test_other_effects_pass_untouched() -> None:
    """The check reads usage records alone."""
    other = Effect(type=EffectType.LOG, payload="hello", plugin_name="acme")

    assert permitted_usage([other], frozenset()) == [other]

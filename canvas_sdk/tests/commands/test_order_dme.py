import json

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.events_pb2 import EventType
from canvas_sdk.commands import OrderDmeCommand
from canvas_sdk.commands.constants import ServiceProvider


def _anchored(command: OrderDmeCommand) -> OrderDmeCommand:
    """Attach note and command ids after construction so they stay out of the payload."""
    command.note_uuid = "note-123"
    command.command_uuid = "cmd-456"
    return command


def test_constantized_key_matches_the_effect_names() -> None:
    """Effect enum names derive from the key, so the two have to agree."""
    assert OrderDmeCommand().constantized_key() == "ORDER_DME"


@pytest.mark.parametrize("field", ["ITEM", "SEND_TO", "INDICATIONS", "ORDERING_PROVIDER"])
def test_every_search_field_has_pre_and_post_search_events(field: str) -> None:
    """home-app emits a field's search events only when both enum names exist."""
    for stage in ("PRE_SEARCH", "POST_SEARCH"):
        assert f"ORDER_DME__{field}__{stage}" in EventType.DESCRIPTOR.values_by_name


def test_originate_carries_every_field() -> None:
    """Originating sends each set field under its SDK name."""
    effect = _anchored(
        OrderDmeCommand(
            dme_product_id="0f2c1c1e-3d1a-4a5b-9a51-5c3c2d1b0a99",
            diagnosis_codes=["N186"],
            quantity=1,
            length_of_need="Lifetime",
            ordering_provider_key="abc123",
        )
    ).originate()

    assert effect.type == EffectType.ORIGINATE_ORDER_DME_COMMAND
    assert json.loads(effect.payload)["data"] == {
        "dme_product_id": "0f2c1c1e-3d1a-4a5b-9a51-5c3c2d1b0a99",
        "diagnosis_codes": ["N186"],
        "quantity": 1,
        "length_of_need": "Lifetime",
        "ordering_provider_key": "abc123",
    }


def test_free_text_item_is_sent() -> None:
    """An off-formulary item travels as free text."""
    effect = _anchored(OrderDmeCommand(free_text_item="Bariatric shower chair")).originate()

    assert json.loads(effect.payload)["data"] == {"free_text_item": "Bariatric shower chair"}


def test_product_and_free_text_are_mutually_exclusive() -> None:
    """An order carries one item, so naming both is refused."""
    with pytest.raises(ValidationError, match="either dme_product_id or free_text_item"):
        OrderDmeCommand(dme_product_id="x", free_text_item="y")


def test_service_provider_is_serialized() -> None:
    """The supplier is sent as a plain dict."""
    provider = ServiceProvider(
        first_name="Acme",
        last_name="Medical Supply",
        specialty="Durable Medical Equipment",
        practice_name="Acme",
        business_fax="5555550100",
    )
    effect = _anchored(OrderDmeCommand(service_provider=provider)).originate()

    assert json.loads(effect.payload)["data"]["service_provider"]["first_name"] == "Acme"


@pytest.mark.parametrize("quantity", [0, -1])
def test_quantity_must_be_positive(quantity: int) -> None:
    """Quantity counts whole units, so zero or less is refused."""
    with pytest.raises(ValidationError, match="quantity"):
        OrderDmeCommand(quantity=quantity)


def test_length_of_need_is_capped_at_the_column_length() -> None:
    """Length of need is free text stored in a 255 character column."""
    with pytest.raises(ValidationError, match="length_of_need"):
        OrderDmeCommand(length_of_need="x" * 256)


def test_sign_returns_the_sign_effect() -> None:
    """Sign is available on a staged order."""
    command = OrderDmeCommand()
    command.command_uuid = "cmd-456"

    assert command.sign().type == EffectType.SIGN_ORDER_DME_COMMAND


def test_lifecycle_effects() -> None:
    """Commit, edit, delete and enter-in-error target the existing command."""
    command = _anchored(OrderDmeCommand(quantity=1))

    assert command.commit().type == EffectType.COMMIT_ORDER_DME_COMMAND
    assert command.edit().type == EffectType.EDIT_ORDER_DME_COMMAND
    assert command.delete().type == EffectType.DELETE_ORDER_DME_COMMAND
    assert command.enter_in_error().type == EffectType.ENTER_IN_ERROR_ORDER_DME_COMMAND

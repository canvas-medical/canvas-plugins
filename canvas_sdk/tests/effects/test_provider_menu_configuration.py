import json

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.provider_menu_configuration import ProviderMenuConfiguration


def test_items_enum_values() -> None:
    """Test that the Items enum has expected values."""
    Items = ProviderMenuConfiguration.Items
    assert Items.SCHEDULE.value == "schedule"
    assert Items.PATIENTS.value == "patients"
    assert Items.REVENUE.value == "revenue"
    assert Items.POPULATIONS.value == "populations"
    assert Items.CAMPAIGNS.value == "campaigns"
    assert Items.DATA_INTEGRATION.value == "data_integration"
    assert Items.QUESTIONNAIRE_BUILDER.value == "questionnaire_builder"
    assert Items.SETTINGS.value == "settings"
    assert Items.MULTI_FACTOR_AUTHENTICATION.value == "multi_factor_authentication"
    assert Items.CHANGELOG.value == "changelog"
    assert Items.HELP_CENTER.value == "help_center"


def test_apply_uses_the_show_provider_menu_items_effect_type() -> None:
    """Test that the applied effect is typed as SHOW_PROVIDER_MENU_ITEMS."""
    Items = ProviderMenuConfiguration.Items
    effect = ProviderMenuConfiguration(items=[Items.PATIENTS]).apply()

    assert effect.type == EffectType.SHOW_PROVIDER_MENU_ITEMS


def test_apply_with_single_item() -> None:
    """Test apply with a single item."""
    Items = ProviderMenuConfiguration.Items
    config = ProviderMenuConfiguration(items=[Items.PATIENTS])
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload == {"data": {"items": ["patients"]}}


def test_apply_with_multiple_items() -> None:
    """Test apply with multiple items."""
    Items = ProviderMenuConfiguration.Items
    config = ProviderMenuConfiguration(items=[Items.PATIENTS, Items.CAMPAIGNS, Items.SETTINGS])
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload == {"data": {"items": ["patients", "campaigns", "settings"]}}


def test_apply_with_all_items() -> None:
    """Test apply with all items."""
    Items = ProviderMenuConfiguration.Items
    config = ProviderMenuConfiguration(items=list(Items))
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload["data"]["items"] == [item.value for item in Items]


def test_apply_omitting_schedule() -> None:
    """Test the scheduling-plugin case: every item except SCHEDULE."""
    Items = ProviderMenuConfiguration.Items
    config = ProviderMenuConfiguration(items=[item for item in Items if item is not Items.SCHEDULE])
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert "schedule" not in payload["data"]["items"]
    assert len(payload["data"]["items"]) == len(Items) - 1


def test_apply_with_empty_items_hides_every_native_item() -> None:
    """Test that an empty items list is allowed and hides every native item."""
    config = ProviderMenuConfiguration(items=[])
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload == {"data": {"items": []}}


def test_apply_with_unknown_item_raises_validation_error() -> None:
    """Test that an item outside the Items enum raises a validation error."""
    with pytest.raises(ValidationError):
        ProviderMenuConfiguration(items=["not_a_menu_item"])  # type: ignore[list-item]


def test_values_property() -> None:
    """Test that the values property returns the correct dict."""
    Items = ProviderMenuConfiguration.Items
    config = ProviderMenuConfiguration(items=[Items.PATIENTS, Items.HELP_CENTER])
    assert config.values == {"items": ["patients", "help_center"]}

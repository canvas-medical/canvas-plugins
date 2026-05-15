import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.patient_note_header_dropdown_configuration import (
    PatientNoteHeaderDropdownConfiguration,
)


def test_items_enum_values() -> None:
    """Test that the Items enum has expected values."""
    Items = PatientNoteHeaderDropdownConfiguration.Items
    assert Items.LINK_TO_PHONE.value == "link_to_phone"
    assert Items.SOAP.value == "soap"
    assert Items.APSO.value == "apso"
    assert Items.CHANGE_LOCATION.value == "change_location"
    assert Items.CHANGE_PROVIDER.value == "change_provider"
    assert Items.CHANGE_DATE_OF_SERVICE.value == "change_date_of_service"
    assert Items.PRINT_SUPERBILL.value == "print_superbill"
    assert Items.PRINT_ROOMING_SHEET.value == "print_rooming_sheet"
    assert Items.PRINT_AFTER_VISIT_SUMMARY.value == "print_after_visit_summary"
    assert Items.COPY_LINK.value == "copy_link"
    assert Items.PRINT_NOTE.value == "print_note"
    assert Items.FAX_NOTE.value == "fax_note"
    assert Items.MOVE_COMMANDS.value == "move_commands"


def test_apply_with_single_item() -> None:
    """Test apply with a single item."""
    Items = PatientNoteHeaderDropdownConfiguration.Items
    config = PatientNoteHeaderDropdownConfiguration(items=[Items.SOAP])
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload == {"data": {"items": ["soap"]}}


def test_apply_with_multiple_items() -> None:
    """Test apply with multiple items."""
    Items = PatientNoteHeaderDropdownConfiguration.Items
    config = PatientNoteHeaderDropdownConfiguration(
        items=[Items.SOAP, Items.COPY_LINK, Items.PRINT_NOTE]
    )
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload == {"data": {"items": ["soap", "copy_link", "print_note"]}}


def test_apply_with_all_items() -> None:
    """Test apply with all items."""
    Items = PatientNoteHeaderDropdownConfiguration.Items
    config = PatientNoteHeaderDropdownConfiguration(items=list(Items))
    effect = config.apply()

    payload = json.loads(effect.payload)
    assert payload["data"]["items"] == [item.value for item in Items]


def test_apply_with_empty_items_raises_validation_error() -> None:
    """Test that an empty items list raises a validation error."""
    with pytest.raises(ValidationError) as exc_info:
        PatientNoteHeaderDropdownConfiguration(items=[])

    assert "List should have at least 1 item" in str(exc_info.value)


def test_values_property() -> None:
    """Test that the values property returns the correct dict."""
    Items = PatientNoteHeaderDropdownConfiguration.Items
    config = PatientNoteHeaderDropdownConfiguration(items=[Items.CHANGE_LOCATION, Items.FAX_NOTE])
    assert config.values == {"items": ["change_location", "fax_note"]}

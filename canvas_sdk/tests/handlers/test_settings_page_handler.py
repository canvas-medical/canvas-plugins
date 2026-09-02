"""Tests for the SettingsPageHandler and its companion SettingsPageForm effect."""

import json

import pytest
from django.core.exceptions import ImproperlyConfigured

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_sdk.effects import Effect
from canvas_sdk.effects.form import FormField, InputType
from canvas_sdk.effects.settings_page_form import SettingsPageForm
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.settings_page import SettingsPageHandler


class DemoSettings(SettingsPageHandler):
    """Concrete implementation for testing."""

    SECTION_KEY = "demo"
    SECTION_TITLE = "Demo Section"
    SECTION_CATEGORY = "Clinical"
    SECTION_DESCRIPTION = "A short description."

    def render(self) -> SettingsPageForm:
        """Render."""
        return SettingsPageForm(
            section_key=self.SECTION_KEY,
            title=self.SECTION_TITLE,
            form_fields=[FormField(key="name", label="Name", required=True)],
        )


class MinimalDefaultsSettings(SettingsPageHandler):
    """Handler that omits title/category in the form to exercise compute() defaults."""

    SECTION_KEY = "minimal"
    SECTION_TITLE = "Minimal"
    SECTION_CATEGORY = "Workflow"
    SECTION_DESCRIPTION = "fills defaults"

    def render(self) -> SettingsPageForm:
        """Render."""
        return SettingsPageForm(
            form_fields=[FormField(key="x", label="X")],
        )


def make_event(section_key: str | None = None) -> Event:
    """Make event."""
    context = json.dumps({"section_key": section_key}) if section_key is not None else ""
    return Event(
        EventRequest(
            type=EventType.INSTANCE_CONFIG__GET_SETTINGS_PAGE,
            context=context,
        )
    )


def test_missing_section_key_raises() -> None:
    """Missing section key raises."""
    with pytest.raises(ImproperlyConfigured, match="must define"):

        class NoKey(SettingsPageHandler):
            def render(self) -> SettingsPageForm:
                return SettingsPageForm()


def test_responds_to_contains_settings_page_event() -> None:
    """Responds to contains settings page event."""
    assert (
        EventType.Name(EventType.INSTANCE_CONFIG__GET_SETTINGS_PAGE)
        in SettingsPageHandler.RESPONDS_TO
    )


def test_accept_event_true_for_matching_section_key() -> None:
    """Accept event true for matching section key."""
    handler = DemoSettings(make_event("demo"))
    assert handler.accept_event() is True


def test_accept_event_false_for_different_section_key() -> None:
    """Accept event false for different section key."""
    handler = DemoSettings(make_event("other"))
    assert handler.accept_event() is False


def test_compute_returns_settings_page_form_effect() -> None:
    """Compute returns settings page form effect."""
    handler = DemoSettings(make_event("demo"))
    effects = handler.compute()

    assert len(effects) == 1
    assert isinstance(effects[0], Effect)
    assert EffectType.Name(effects[0].type) == "SHOW_SETTINGS_PAGE_FORM"

    data = json.loads(effects[0].payload)["data"]
    assert data["section_key"] == "demo"
    assert data["title"] == "Demo Section"
    assert data["category"] == "Clinical"
    assert len(data["form"]) == 1


def test_compute_fills_defaults_when_form_omits_them() -> None:
    """Compute fills defaults when form omits them."""
    handler = MinimalDefaultsSettings(make_event("minimal"))
    effects = handler.compute()

    data = json.loads(effects[0].payload)["data"]
    assert data["section_key"] == "minimal"
    assert data["title"] == "Minimal"
    assert data["category"] == "Workflow"
    assert data["description"] == "fills defaults"


def test_settings_page_form_requires_section_key_title_and_fields() -> None:
    """Settings page form requires section key title and fields."""
    from pydantic_core import ValidationError

    with pytest.raises(ValidationError):
        SettingsPageForm(section_key="demo", title="Demo", form_fields=[]).apply()


def test_form_field_widget_primitives_serialize_correctly() -> None:
    """Each new widget type produces the expected `type` value in the payload."""
    widgets = [
        (InputType.CHECKLIST_PICKER, "checklist_picker"),
        (InputType.TOGGLE_CARDS, "toggle_cards"),
        (InputType.COLOR_PICKER, "color_picker"),
        (InputType.GRADIENT_BUILDER, "gradient_builder"),
        (InputType.ICON_PICKER, "icon_picker"),
        (InputType.ADDRESS_LIST, "address_list"),
        (InputType.INLINE_TABLE, "inline_table"),
        (InputType.STATUS_BADGE, "status_badge"),
        (InputType.KEY_PILL, "key_pill"),
        (InputType.BOOLEAN, "boolean"),
        (InputType.NUMBER, "number"),
        (InputType.EMAIL, "email"),
        (InputType.PHONE, "phone"),
        (InputType.URL, "url"),
        (InputType.FILE, "file"),
        (InputType.TEXTAREA, "textarea"),
    ]
    for widget_enum, wire_value in widgets:
        field = FormField(key="x", label="X", type=widget_enum)
        assert field.to_dict()["type"] == wire_value


def test_form_field_legacy_shape_is_preserved_when_extensions_unused() -> None:
    """A field with only the legacy attributes serializes to the legacy keyset."""
    field = FormField(key="x", label="X", type=InputType.TEXT)
    assert set(field.to_dict().keys()) == {
        "key",
        "label",
        "required",
        "editable",
        "type",
        "options",
        "value",
    }


def test_form_field_widget_config_is_emitted_when_set() -> None:
    """Form field widget config is emitted when set."""
    field = FormField(
        key="addrs",
        label="Addresses",
        type=InputType.ADDRESS_LIST,
        widget_config={"allowed_uses": ["work", "billing"]},
    )
    out = field.to_dict()
    assert out["widget_config"] == {"allowed_uses": ["work", "billing"]}


def test_form_field_options_allowed_on_checklist_and_toggle() -> None:
    """Options must validate against any option-bearing widget, not just SELECT."""
    from canvas_sdk.effects.command_metadata import (
        CommandMetadataCreateFormEffect,
    )

    # Should not raise — CHECKLIST_PICKER accepts options
    effect = CommandMetadataCreateFormEffect(
        command_uuid="cmd-uuid",
        form_fields=[
            FormField(
                key="roles", label="Roles", type=InputType.CHECKLIST_PICKER, options=["A", "B"]
            ),
        ],
    )
    effect.apply()  # no exception

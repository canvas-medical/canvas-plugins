import json

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import (
    ApplicationScope,
    EmbeddedApplication,
    MenuPosition,
)


class ExampleProviderMenuApplication(EmbeddedApplication):
    """A provider menu entry."""

    NAME = "Care gaps"
    SCOPE = ApplicationScope.PROVIDER_MENU
    IDENTIFIER = "test_plugin__care_gaps"

    def on_open(self) -> Effect | list[Effect]:
        """Launch the application."""
        return [LaunchModalEffect(url="https://example.com/care-gaps").apply()]


class BottomMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry pinned to the bottom group."""

    MENU_POSITION = MenuPosition.BOTTOM


class ExamplePanelApplication(EmbeddedApplication):
    """A panel bar entry."""

    NAME = "Inbox"
    SCOPE = ApplicationScope.PANEL
    IDENTIFIER = "test_plugin__inbox"
    ICON_URL = "https://example.com/icon.png"

    def on_open(self) -> Effect | list[Effect]:
        """Launch the application."""
        return [LaunchModalEffect(url="https://example.com/inbox").apply()]


class InlinePanelApplication(ExamplePanelApplication):
    """A panel entry rendered inline in the bar rather than in the drawer."""

    SHOW_IN_PANEL = True


class BadgedMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry reporting a badge count."""

    def compute_notification_badge(self) -> int | None:
        """Report a fixed count."""
        return 7


class IconlessPanelApplication(EmbeddedApplication):
    """A panel entry that declares no icon."""

    NAME = "Iconless"
    SCOPE = ApplicationScope.PANEL
    IDENTIFIER = "test_plugin__iconless"

    def on_open(self) -> Effect | list[Effect]:
        """Nothing to launch."""
        return []


class ConditionalMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry visible only for a patient in context."""

    def visible(self) -> bool:
        """Show only when a patient is in context."""
        return self.event.context.get("patient") is not None


def _on_get(scope: str, **extra_context: object) -> Event:
    """An APPLICATION__ON_GET event carrying the given scope."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__ON_GET,
            context=json.dumps({"scope": scope, **extra_context}),
        )
    )


def _payload(app: EmbeddedApplication) -> dict:
    """Compute the application and return its single effect's data payload."""
    result = app.compute()
    assert len(result) == 1
    assert result[0].type == EffectType.SHOW_APPLICATION
    return json.loads(result[0].payload)["data"]


@pytest.mark.parametrize(
    "scope,expected",
    [
        (ApplicationScope.PROVIDER_MENU, "provider_menu"),
        (ApplicationScope.PANEL, "panel"),
    ],
    ids=["provider-menu", "panel"],
)
def test_launcher_scopes_have_stable_values(scope: ApplicationScope, expected: str) -> None:
    """The scope strings cross the wire to home-app, so they are part of the contract."""
    assert scope.value == expected


def test_provider_menu_reports_its_menu_position() -> None:
    """Which group of the side menu an entry joins travels on the ON_GET effect."""
    assert _payload(ExampleProviderMenuApplication(_on_get("provider_menu")))["menu_position"] == (
        "top"
    )
    assert _payload(BottomMenuApplication(_on_get("provider_menu")))["menu_position"] == "bottom"


def test_an_unknown_menu_position_raises() -> None:
    """The two groups are the only ones the side menu has."""

    class Sideways(ExampleProviderMenuApplication):
        MENU_POSITION = "middle"  # type: ignore[assignment]

    with pytest.raises(ValueError, match="middle"):
        Sideways(_on_get("provider_menu")).compute()


def test_provider_menu_needs_no_icon() -> None:
    """The side menu renders the name as text, so an icon is optional there."""
    payload = _payload(ExampleProviderMenuApplication(_on_get("provider_menu")))

    assert payload["icon_url"] is None
    assert payload["name"] == "Care gaps"


def test_panel_reports_its_icon_and_placement() -> None:
    """The panel bar renders an icon, and show_in_panel picks inline bar over the drawer."""
    drawer = _payload(ExamplePanelApplication(_on_get("panel")))
    assert drawer["icon_url"] == "https://example.com/icon.png"
    assert drawer["show_in_panel"] is False

    inline = _payload(InlinePanelApplication(_on_get("panel")))
    assert inline["show_in_panel"] is True


def test_a_panel_application_declaring_no_icon_raises() -> None:
    """The panel bar renders nothing but the icon, so a missing one is a programming error."""
    with pytest.raises(NotImplementedError, match="ICON_URL"):
        IconlessPanelApplication(_on_get("panel")).compute()


def test_another_scope_may_omit_the_icon() -> None:
    """Only the panel bar requires one, so the check must not fire for other surfaces."""

    class NoteTool(EmbeddedApplication):
        NAME = "Note tool"
        SCOPE = ApplicationScope.NOTE

        def on_open(self) -> Effect | list[Effect]:
            return []

    assert _payload(NoteTool(_on_get("note")))["icon_url"] is None


def test_badge_count_travels_on_the_on_get_effect() -> None:
    """The count rides the response that already ran, rather than a second round trip."""
    assert _payload(BadgedMenuApplication(_on_get("provider_menu")))["badge_count"] == 7


def test_no_badge_stays_absent() -> None:
    """The default compute_notification_badge reports nothing, which must not become a zero."""
    assert _payload(ExampleProviderMenuApplication(_on_get("provider_menu")))["badge_count"] is None


def test_a_directly_emitted_badge_event_still_returns_nothing() -> None:
    """The row-free badge path stays closed; the count only travels on ON_GET."""
    event = Event(
        EventRequest(
            type=EventType.APPLICATION__GET_NOTIFICATION_BADGE,
            target="test_plugin__care_gaps",
            context=json.dumps({}),
        )
    )
    assert BadgedMenuApplication(event).compute() == []


def test_invisible_launcher_returns_no_effects() -> None:
    """visible() is the whole point: no patient in context, no entry."""
    assert ConditionalMenuApplication(_on_get("provider_menu")).compute() == []


def test_visible_launcher_returns_its_effect() -> None:
    """With the condition met the entry appears."""
    event = _on_get("provider_menu", patient={"id": "abc"})
    assert _payload(ConditionalMenuApplication(event))["identifier"] == "test_plugin__care_gaps"


@pytest.mark.parametrize(
    "app_class,foreign_scope",
    [
        (ExampleProviderMenuApplication, "panel"),
        (ExamplePanelApplication, "provider_menu"),
    ],
    ids=["provider-menu-asked-for-panel", "panel-asked-for-provider-menu"],
)
def test_a_launcher_stays_silent_for_the_other_menu(
    app_class: type[EmbeddedApplication], foreign_scope: str
) -> None:
    """One class serves one menu; the other menu's request is not its business."""
    assert app_class(_on_get(foreign_scope)).compute() == []


def test_on_open_still_launches() -> None:
    """A launcher is opened by clicking it, which is the inherited Application behaviour."""
    event = Event(
        EventRequest(
            type=EventType.APPLICATION__ON_OPEN,
            target="test_plugin__care_gaps",
            context=json.dumps({}),
        )
    )
    result = ExampleProviderMenuApplication(event).compute()

    assert len(result) == 1
    assert result[0].type == EffectType.LAUNCH_MODAL

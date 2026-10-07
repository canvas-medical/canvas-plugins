import json
from typing import Any

import pytest
from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import (
    ApplicationScope,
    DockedApplication,
    DockEdge,
    EmbeddedApplication,
    MenuPosition,
    NoteApplication,
    PanelApplication,
    ProviderMenuApplication,
)


class ExampleProviderMenuApplication(ProviderMenuApplication):
    """A provider menu entry."""

    NAME = "Care gaps"
    IDENTIFIER = "test_plugin__care_gaps"

    def on_open(self) -> Effect | list[Effect]:
        """Launch the application."""
        return [LaunchModalEffect(url="https://example.com/care-gaps").apply()]


class BottomMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry pinned to the bottom group."""

    MENU_POSITION = MenuPosition.BOTTOM


class BadgedMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry reporting a badge count."""

    def compute_notification_badge(self) -> int | None:
        """Report a fixed count."""
        return 7


class ConditionalMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry visible only for a patient in context."""

    def visible(self) -> bool:
        """Show only when a patient is in context."""
        return self.event.context.get("patient") is not None


class ExamplePanelApplication(PanelApplication):
    """A panel bar entry, in the drawer by default."""

    NAME = "Inbox"
    IDENTIFIER = "test_plugin__inbox"
    ICON_URL = "https://example.com/icon.png"

    def on_open(self) -> Effect | list[Effect]:
        """Launch the application."""
        return [LaunchModalEffect(url="https://example.com/inbox").apply()]


class InlinePanelApplication(ExamplePanelApplication):
    """A panel entry rendered inline in the bar rather than in the drawer."""

    SHOW_IN_DRAWER = False


class BadgedPanelApplication(ExamplePanelApplication):
    """A panel entry reporting a badge count."""

    def compute_notification_badge(self) -> int | None:
        """Report a fixed count."""
        return 4


def _on_get(scope: str, **extra_context: object) -> Event:
    """An APPLICATION__ON_GET event carrying the given scope."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__ON_GET,
            context=json.dumps({"scope": scope, **extra_context}),
        )
    )


def _payload(app: EmbeddedApplication) -> dict[str, Any]:
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


@pytest.mark.parametrize(
    "app_class,expected_scope",
    [
        (ProviderMenuApplication, ApplicationScope.PROVIDER_MENU),
        (PanelApplication, ApplicationScope.PANEL),
    ],
    ids=["provider-menu", "panel"],
)
def test_each_launcher_pins_its_scope(
    app_class: type[EmbeddedApplication], expected_scope: ApplicationScope
) -> None:
    """A launcher needs no SCOPE of its own, the same way a dock does not."""
    assert expected_scope == app_class.SCOPE


# --- the chrome each surface reports -----------------------------------------------


def test_provider_menu_reports_its_menu_position() -> None:
    """Which group of the side menu an entry joins travels on the ON_GET effect."""
    assert _payload(ExampleProviderMenuApplication(_on_get("provider_menu")))["menu_position"] == (
        "top"
    )
    assert _payload(BottomMenuApplication(_on_get("provider_menu")))["menu_position"] == "bottom"


def test_provider_menu_needs_no_icon() -> None:
    """The side menu renders the name as text, so an icon is optional there."""
    payload = _payload(ExampleProviderMenuApplication(_on_get("provider_menu")))

    assert payload["icon_url"] is None
    assert payload["name"] == "Care gaps"


def test_an_unknown_menu_position_raises() -> None:
    """The two groups are the only ones the side menu has."""

    class Sideways(ExampleProviderMenuApplication):
        MENU_POSITION = "middle"  # type: ignore[assignment]

    with pytest.raises(ValueError, match="middle"):
        Sideways(_on_get("provider_menu")).compute()


def test_panel_defaults_to_the_drawer() -> None:
    """SHOW_IN_DRAWER defaults true, so an entry lands behind the grid button."""
    payload = _payload(ExamplePanelApplication(_on_get("panel")))

    assert payload["icon_url"] == "https://example.com/icon.png"
    assert payload["show_in_panel"] is False


def test_panel_can_render_inline_instead() -> None:
    """Clearing SHOW_IN_DRAWER puts the icon in the bar itself."""
    assert _payload(InlinePanelApplication(_on_get("panel")))["show_in_panel"] is True


@pytest.mark.parametrize(
    "app_class,expected",
    [
        (BadgedMenuApplication, 7),
        (BadgedPanelApplication, 4),
    ],
    ids=["provider-menu", "panel"],
)
def test_both_launcher_surfaces_report_a_badge(
    app_class: type[EmbeddedApplication], expected: int
) -> None:
    """Both menus draw a badge, so both must carry the count.

    The panel bar renders one for an inline icon and for a drawer entry alike, so leaving
    it off the panel surface would silently drop every panel badge.
    """
    scope = app_class.SCOPE
    assert _payload(app_class(_on_get(scope)))["badge_count"] == expected


def test_no_badge_stays_absent() -> None:
    """The default compute_notification_badge reports nothing, which must not become a zero."""
    assert _payload(ExampleProviderMenuApplication(_on_get("provider_menu")))["badge_count"] is None


# --- a panel application must declare an icon --------------------------------------


def test_a_panel_application_declaring_no_icon_raises_at_definition() -> None:
    """The bar renders the icon and nothing else, so a missing one is a programming error.

    It raises when the class is defined, which for a plugin is load time, rather than
    when a provider happens to open the surface.
    """
    with pytest.raises(ImproperlyConfigured, match="ICON_URL"):

        class Iconless(PanelApplication):
            NAME = "Iconless"

            def on_open(self) -> Effect | list[Effect]:
                return []


def test_an_intermediate_base_may_defer_its_icon() -> None:
    """A plugin sharing behaviour across panel entries needs a base without an icon."""

    class SharedBase(PanelApplication):
        abstract = True

        def on_open(self) -> Effect | list[Effect]:
            return [LaunchModalEffect(url="https://example.com/shared").apply()]

    class Leaf(SharedBase):
        NAME = "Leaf"
        ICON_URL = "https://example.com/leaf.png"

    assert _payload(Leaf(_on_get("panel")))["icon_url"] == "https://example.com/leaf.png"


def test_an_abstract_base_does_not_exempt_its_subclasses() -> None:
    """`abstract` applies to the class that sets it, never to what inherits from it."""

    class SharedBase(PanelApplication):
        abstract = True

        def on_open(self) -> Effect | list[Effect]:
            return []

    with pytest.raises(ImproperlyConfigured, match="ICON_URL"):

        class Leaf(SharedBase):
            NAME = "Leaf"


# --- the NOOP the reviewer flagged: other scopes must not carry launcher chrome ----


@pytest.mark.parametrize(
    "attribute",
    ["ICON_URL", "MENU_POSITION", "SHOW_IN_DRAWER"],
)
@pytest.mark.parametrize(
    "app_class",
    [EmbeddedApplication, DockedApplication, NoteApplication],
    ids=["embedded", "docked", "note"],
)
def test_launcher_chrome_is_absent_from_other_scopes(
    app_class: type[EmbeddedApplication], attribute: str
) -> None:
    """Setting launcher chrome on a dock or a note would do nothing, so it must not exist.

    An attribute that can be assigned and then silently ignored is worse than one that is
    absent, because the author gets no signal at all.
    """
    assert not hasattr(app_class, attribute)


def test_a_note_application_reports_no_launcher_chrome() -> None:
    """A non-launcher surface reports no chrome, so none can reach a menu.

    ``ShowApplicationEffect`` carries a slot for every surface's chrome, so the assertion
    is on the values rather than on which keys exist.
    """

    class NoteTool(NoteApplication):
        NAME = "Note tool"
        IDENTIFIER = "test_plugin__note_tool"

        def on_open(self) -> Effect | list[Effect]:
            return []

    payload = _payload(NoteTool(_on_get("note")))

    assert payload["icon_url"] is None
    assert payload["menu_position"] is None
    assert payload["show_in_panel"] is None
    assert payload["badge_count"] is None


def test_a_docked_application_reports_only_its_placement() -> None:
    """A dock reports its edge and size, and no launcher chrome."""

    class DockTool(DockedApplication):
        NAME = "Dock tool"
        IDENTIFIER = "test_plugin__dock_tool"
        DOCK_EDGE = "left"  # type: ignore[assignment]
        DOCK_SIZE = "320px"

        def on_open(self) -> Effect | list[Effect]:
            return []

    payload = _payload(DockTool(_on_get("docked")))

    assert payload["dock_edge"] == "left"
    assert payload["dock_size"] == "320px"
    assert payload["icon_url"] is None
    assert payload["menu_position"] is None
    assert payload["show_in_panel"] is None


# --- behaviour inherited from EmbeddedApplication ----------------------------------


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


def test_invisible_launcher_reports_that_it_is_hidden() -> None:
    """A launcher menu draws a manifest row that no handler claims, so silence shows it.

    The row's identifier is the handler's class path, so a hidden launcher answers with
    ``visible`` false rather than nothing, and Canvas drops the entry and the row.
    """
    payload = _payload(ConditionalMenuApplication(_on_get("provider_menu")))

    assert payload["identifier"] == "test_plugin__care_gaps"
    assert payload["visible"] is False


def test_a_hidden_launcher_still_reports_its_chrome() -> None:
    """The menu keeps a hidden entry, so it can show it again on a later page."""

    class HiddenBadgedMenuApplication(BadgedMenuApplication):
        def visible(self) -> bool:
            return False

    payload = _payload(HiddenBadgedMenuApplication(_on_get("provider_menu")))

    assert payload["name"] == "Care gaps"
    assert payload["menu_position"] == "top"
    assert payload["badge_count"] == 7


def test_visible_launcher_returns_its_effect() -> None:
    """With the condition met the entry appears."""
    event = _on_get("provider_menu", patient={"id": "abc"})
    payload = _payload(ConditionalMenuApplication(event))

    assert payload["identifier"] == "test_plugin__care_gaps"
    assert payload["visible"] is True


class HiddenNoteApplication(NoteApplication):
    """A note application that hides itself."""

    NAME = "Hidden note tool"

    def visible(self) -> bool:
        """Hide on every page."""
        return False

    def on_open(self) -> Effect | list[Effect]:
        """Launch nothing."""
        return []


class HiddenDockedApplication(DockedApplication):
    """A docked application that hides itself."""

    NAME = "Hidden dock"
    DOCK_EDGE = DockEdge.RIGHT
    DOCK_SIZE = "320px"

    def visible(self) -> bool:
        """Hide on every page."""
        return False

    def on_open(self) -> Effect | list[Effect]:
        """Launch nothing."""
        return []


@pytest.mark.parametrize(
    "app_class",
    [HiddenNoteApplication, HiddenDockedApplication],
    ids=["note", "docked"],
)
def test_a_hidden_non_launcher_scope_stays_silent(
    app_class: type[EmbeddedApplication],
) -> None:
    """Only a launcher menu merges manifest rows, so other scopes have no row to suppress."""
    assert app_class(_on_get(app_class.SCOPE)).compute() == []


# --- a navigation: an untargeted APPLICATION__ON_CONTEXT_CHANGE -----------------------


def _context_change(target: str = "", **context: object) -> Event:
    """An APPLICATION__ON_CONTEXT_CHANGE event; with no target it reports a navigation."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__ON_CONTEXT_CHANGE,
            target=target,
            context=json.dumps(context),
        )
    )


class UnbadgeableMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry whose badge must not be computed."""

    def compute_notification_badge(self) -> int | None:
        """Fail the test if a navigation asks for the count."""
        raise AssertionError("a navigation computed a badge")


class ContextAwareMenuApplication(ExampleProviderMenuApplication):
    """A provider menu entry that reacts to context changes while open."""

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Relaunch with the new page."""
        return [LaunchModalEffect(url="https://example.com/care-gaps?moved").apply()]


@pytest.mark.parametrize(
    "app_class",
    [ExampleProviderMenuApplication, ExamplePanelApplication],
    ids=["provider-menu", "panel"],
)
def test_a_navigation_makes_a_launcher_report_its_entry(
    app_class: type[EmbeddedApplication],
) -> None:
    """The menu replaces the entry by identifier, so the update carries the whole entry."""
    payload = _payload(app_class(_context_change(url="/schedule")))

    assert payload["identifier"] == app_class.IDENTIFIER
    assert payload["name"] == app_class.NAME
    assert payload["visible"] is True


def test_a_navigation_reports_a_launcher_hidden_on_the_new_page() -> None:
    """visible() runs against the new page, and a hidden entry still answers."""
    payload = _payload(ConditionalMenuApplication(_context_change(url="/schedule")))

    assert payload["visible"] is False


def test_a_navigation_shows_a_launcher_its_new_context() -> None:
    """visible() reads the context the navigation carries."""
    event = _context_change(url="/patient/abc", patient={"id": "abc"})

    assert _payload(ConditionalMenuApplication(event))["visible"] is True


def test_a_navigation_computes_no_badge() -> None:
    """A badge costs the plugin a computation, so it travels only on the first load."""
    payload = _payload(UnbadgeableMenuApplication(_context_change(url="/schedule")))

    assert payload["badge_count"] is None


def test_a_navigation_does_not_reach_on_context_change() -> None:
    """on_context_change() is for an open surface, which gets its own targeted event."""
    result = ContextAwareMenuApplication(_context_change(url="/schedule")).compute()

    assert [effect.type for effect in result] == [EffectType.SHOW_APPLICATION]


def test_a_targeted_context_change_reaches_the_open_launcher_only() -> None:
    """An open launcher gets its targeted event as before, with no menu update in it."""
    result = ContextAwareMenuApplication(_context_change(target="test_plugin__care_gaps")).compute()

    assert [effect.type for effect in result] == [EffectType.LAUNCH_MODAL]


@pytest.mark.parametrize(
    "app_class",
    [HiddenNoteApplication, HiddenDockedApplication],
    ids=["note", "docked"],
)
def test_a_navigation_leaves_other_scopes_silent(app_class: type[EmbeddedApplication]) -> None:
    """Only the launcher menus redraw on a navigation."""
    assert app_class(_context_change(url="/schedule")).compute() == []


def test_an_untargeted_open_still_launches_nothing() -> None:
    """Only a context change is untargeted; an open goes to one application."""
    event = Event(
        EventRequest(type=EventType.APPLICATION__ON_OPEN, target="", context=json.dumps({}))
    )

    assert ExampleProviderMenuApplication(event).compute() == []


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

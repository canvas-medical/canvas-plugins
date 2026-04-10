import json

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import ApplicationScope, EmbeddedApplication


class ExampleEmbeddedApplication(EmbeddedApplication):
    """A concrete EmbeddedApplication scoped to 'note' for testing."""

    NAME = "Test Embedded App"
    SCOPE = ApplicationScope.NOTE
    IDENTIFIER = "test_plugin__embedded_app"

    def on_open(self) -> list[Effect]:
        """On open method."""
        return [LaunchModalEffect(url="https://example.com/embedded").apply()]

    def on_context_change(self) -> list[Effect]:
        """On context change method."""
        return [LaunchModalEffect(url="https://example.com/context").apply()]


class CustomVisibilityApp(EmbeddedApplication):
    """An EmbeddedApplication with custom visibility logic."""

    NAME = "Custom Visibility"
    SCOPE = ApplicationScope.NOTE

    def visible(self) -> bool:
        """Return True if the application is visible."""
        return self.event.context.get("show_app") is True

    def on_open(self) -> list[Effect]:
        """On open method."""
        return []


class DefaultOpenApp(EmbeddedApplication):
    """An EmbeddedApplication that opens by default with custom priority."""

    NAME = "Default Open"
    SCOPE = ApplicationScope.NOTE
    PRIORITY = 10

    def open_by_default(self) -> bool:
        """Application open by default."""
        return True

    def on_open(self) -> list[Effect]:
        """On open method."""
        return []


class NoIdentifierApp(EmbeddedApplication):
    """An EmbeddedApplication without an explicit IDENTIFIER."""

    NAME = "No ID"
    SCOPE = ApplicationScope.NOTE

    def on_open(self) -> list[Effect]:
        """On open method."""
        return []


@pytest.mark.parametrize(
    "member,expected_value",
    [
        (ApplicationScope.NOTE, "note"),
        (ApplicationScope.PROVIDER_COMPANION_GLOBAL, "provider_companion_global"),
        (
            ApplicationScope.PROVIDER_COMPANION_PATIENT_SPECIFIC,
            "provider_companion_patient_specific",
        ),
        (ApplicationScope.PROVIDER_COMPANION_NOTE_SPECIFIC, "provider_companion_note_specific"),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_application_scope_values(member: ApplicationScope, expected_value: str) -> None:
    """Verify ApplicationScope enum members have the correct string values."""
    assert member == expected_value
    assert member.value == expected_value


def _make_event(
    event_type: EventType,
    target: str = "",
    context: dict | None = None,
) -> Event:
    """Create an Event from the given type, target, and context."""
    return Event(
        EventRequest(
            type=event_type,
            target=target,
            context=json.dumps(context or {}),
        )
    )


def _make_on_get_event(scope: str = "note", **extra_context: object) -> Event:
    """Create an APPLICATION__ON_GET event with the given scope and optional extra context."""
    return _make_event(EventType.APPLICATION__ON_GET, context={"scope": scope, **extra_context})


def test_embedded_application_is_abstract() -> None:
    """Verify EmbeddedApplication cannot be instantiated directly."""
    with pytest.raises(TypeError):
        EmbeddedApplication(  # type: ignore[abstract]
            _make_on_get_event()
        )


def test_on_get_returns_show_application_effect() -> None:
    """Verify ON_GET returns a SHOW_APPLICATION effect with the correct payload."""
    app = ExampleEmbeddedApplication(_make_on_get_event())
    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SHOW_APPLICATION
    payload = json.loads(result[0].payload)["data"]
    assert payload["name"] == "Test Embedded App"
    assert payload["identifier"] == "test_plugin__embedded_app"
    assert payload["open_by_default"] is False
    assert payload["priority"] == 0


def test_on_get_respects_open_by_default_and_priority() -> None:
    """Verify ON_GET includes open_by_default and priority in the effect payload."""
    app = DefaultOpenApp(_make_on_get_event())
    result = app.compute()

    assert len(result) == 1
    payload = json.loads(result[0].payload)["data"]
    assert payload["open_by_default"] is True
    assert payload["priority"] == 10


@pytest.mark.parametrize(
    "scope,extra_context,app_class,reason",
    [
        ("chart", {}, ExampleEmbeddedApplication, "scope does not match"),
        ("note", {}, CustomVisibilityApp, "visible() returns False"),
        ("chart", {"show_app": True}, CustomVisibilityApp, "scope mismatch overrides visible()"),
    ],
    ids=["wrong-scope", "not-visible", "scope-overrides-visible"],
)
def test_on_get_returns_empty(
    scope: str,
    extra_context: dict,
    app_class: type[EmbeddedApplication],
    reason: str,
) -> None:
    """Verify ON_GET returns no effects when the application should not be shown."""
    app = app_class(_make_on_get_event(scope=scope, **extra_context))
    assert app.compute() == [], reason


def test_on_get_with_custom_visibility() -> None:
    """Verify ON_GET respects custom visible() logic when scope matches."""
    app = CustomVisibilityApp(_make_on_get_event(scope="note", show_app=True))
    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SHOW_APPLICATION


@pytest.mark.parametrize(
    "app_class,expected_identifier",
    [
        (ExampleEmbeddedApplication, "test_plugin__embedded_app"),
        (
            NoIdentifierApp,
            f"{NoIdentifierApp.__module__}:{NoIdentifierApp.__qualname__}",
        ),
    ],
    ids=["explicit-identifier", "fallback-to-module-qualname"],
)
def test_identifier_resolution(
    app_class: type[EmbeddedApplication], expected_identifier: str
) -> None:
    """Verify identifier uses IDENTIFIER when set, otherwise falls back to module:qualname."""
    app = app_class(_make_on_get_event())
    assert app.identifier == expected_identifier


def test_on_open_dispatches_to_on_open() -> None:
    """Verify ON_OPEN dispatches to on_open() when the target matches."""
    target = "test_plugin__embedded_app"
    event = _make_event(EventType.APPLICATION__ON_OPEN, target=target)
    app = ExampleEmbeddedApplication(event)
    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.LAUNCH_MODAL


def test_on_open_returns_empty_when_target_does_not_match() -> None:
    """Verify ON_OPEN returns no effects when the target does not match."""
    event = _make_event(EventType.APPLICATION__ON_OPEN, target="wrong")
    app = ExampleEmbeddedApplication(event)
    assert app.compute() == []


def test_on_context_change_dispatches_when_target_matches() -> None:
    """Verify ON_CONTEXT_CHANGE dispatches to on_context_change() when the target matches."""
    target = "test_plugin__embedded_app"
    event = _make_event(EventType.APPLICATION__ON_CONTEXT_CHANGE, target=target)
    app = ExampleEmbeddedApplication(event)
    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.LAUNCH_MODAL


def test_on_context_change_returns_empty_when_target_does_not_match() -> None:
    """Verify ON_CONTEXT_CHANGE returns no effects when the target does not match."""
    event = _make_event(EventType.APPLICATION__ON_CONTEXT_CHANGE, target="wrong")
    app = ExampleEmbeddedApplication(event)
    assert app.compute() == []


def test_unknown_event_type_returns_empty() -> None:
    """Verify compute returns no effects for an unhandled event type."""
    target = "test_plugin__embedded_app"
    event = _make_event(EventType.UNKNOWN, target=target)
    app = ExampleEmbeddedApplication(event)
    assert app.compute() == []

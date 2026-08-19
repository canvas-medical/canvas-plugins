import json

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import ApplicationScope, DockedApplication, DockEdge


class ExampleDockedApplication(DockedApplication):
    """A concrete DockedApplication for testing."""

    NAME = "Patient list"
    IDENTIFIER = "test_plugin__dock"
    DOCK_EDGE = DockEdge.LEFT
    DOCK_SIZE = "320px"

    def on_open(self) -> Effect | list[Effect]:
        """Mount the pane into the dock layer."""
        return [
            LaunchModalEffect(
                url="https://example.com/pane",
                target=LaunchModalEffect.TargetType.DOCKED_PANE,
            ).apply()
        ]


class BareDock(DockedApplication):
    """A dock that declares no placement at all."""

    NAME = "Bare"
    IDENTIFIER = "test_plugin__bare_dock"

    def on_open(self) -> Effect | list[Effect]:
        """Nothing to mount."""
        return []


def _on_get() -> Event:
    """An APPLICATION__ON_GET event carrying the docked scope."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__ON_GET,
            context=json.dumps({"scope": "docked"}),
        )
    )


def _payload(app: DockedApplication) -> dict:
    """Compute the application and return its single effect's data payload."""
    result = app.compute()
    assert len(result) == 1
    assert result[0].type == EffectType.SHOW_APPLICATION
    return json.loads(result[0].payload)["data"]


def test_docked_application_pins_the_docked_scope() -> None:
    """A dock needs no SCOPE of its own, the same way its siblings do not."""
    assert DockedApplication.SCOPE == ApplicationScope.DOCKED


def test_on_get_reports_its_placement() -> None:
    """Where the pane goes travels on the ON_GET effect, not in the manifest."""
    payload = _payload(ExampleDockedApplication(_on_get()))

    assert payload["dock_edge"] == "left"
    assert payload["dock_size"] == "320px"


def test_a_dock_always_opens() -> None:
    """A dock has no launcher entry, so Canvas must mount it without being asked."""
    payload = _payload(ExampleDockedApplication(_on_get()))

    assert payload["open_by_default"] is True


def test_a_dock_declaring_no_placement_raises() -> None:
    """A missing edge is a programming error, not a pane that quietly never appears."""
    with pytest.raises(NotImplementedError, match="DOCK_EDGE"):
        BareDock(_on_get()).compute()


def test_an_unknown_edge_raises() -> None:
    """The four edges are the only tracks the dock layer has."""

    class Sideways(ExampleDockedApplication):
        DOCK_EDGE = "middle"  # type: ignore[assignment]

    with pytest.raises(ValueError, match="middle"):
        Sideways(_on_get()).compute()


def test_wrong_scope_returns_no_effects() -> None:
    """A dock stays silent when Canvas is asking about another surface."""
    event = Event(
        EventRequest(
            type=EventType.APPLICATION__ON_GET,
            context=json.dumps({"scope": "note"}),
        )
    )
    assert ExampleDockedApplication(event).compute() == []

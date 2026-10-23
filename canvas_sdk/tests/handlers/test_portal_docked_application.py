import json

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import (
    ApplicationScope,
    DockEdge,
    PortalDockedApplication,
)


class PortalFooter(PortalDockedApplication):
    """A concrete PortalDockedApplication for testing."""

    NAME = "Footer"
    IDENTIFIER = "test_plugin__portal_footer"
    DOCK_EDGE = DockEdge.BOTTOM
    DOCK_SIZE = "64px"

    def on_open(self) -> Effect | list[Effect]:
        """Render the footer band."""
        return [
            LaunchModalEffect(
                content="<p>Open 9 to 5</p>",
                target=LaunchModalEffect.TargetType.DOCKED_PANE,
            ).apply()
        ]


def _on_get(scope: str = "portal_docked") -> Event:
    """An APPLICATION__ON_GET event carrying the given scope."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__ON_GET,
            context=json.dumps({"scope": scope}),
        )
    )


def test_portal_docked_application_pins_the_portal_docked_scope() -> None:
    """A portal dock answers the portal's scope, not the provider dock scope."""
    assert PortalDockedApplication.SCOPE == ApplicationScope.PORTAL_DOCKED


@pytest.mark.parametrize("edge", [DockEdge.TOP, DockEdge.BOTTOM])
def test_on_get_reports_its_placement(edge: DockEdge) -> None:
    """The edge and the height travel on the ON_GET effect."""

    class Band(PortalFooter):
        DOCK_EDGE = edge

    result = Band(_on_get()).compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SHOW_APPLICATION
    payload = json.loads(result[0].payload)["data"]
    assert payload["dock_edge"] == edge.value
    assert payload["dock_size"] == "64px"
    assert payload["open_by_default"] is True


@pytest.mark.parametrize("edge", [DockEdge.LEFT, DockEdge.RIGHT])
def test_a_side_edge_raises(edge: DockEdge) -> None:
    """The portal has bands only at the top and the bottom."""

    class Sideways(PortalFooter):
        DOCK_EDGE = edge

    with pytest.raises(ValueError, match="top or bottom"):
        Sideways(_on_get()).compute()


def test_provider_dock_scope_returns_no_effects() -> None:
    """A portal dock stays silent when the provider shell asks for its docks."""
    assert PortalFooter(_on_get("docked")).compute() == []


def test_on_open_returns_the_band_content() -> None:
    """ON_OPEN delegates to on_open, which supplies what the band renders."""
    event = Event(
        EventRequest(
            type=EventType.APPLICATION__ON_OPEN,
            target="test_plugin__portal_footer",
            context=json.dumps({"scope": "portal_docked"}),
        )
    )

    result = PortalFooter(event).compute()

    assert len(result) == 1
    assert result[0].type == EffectType.LAUNCH_MODAL
    assert json.loads(result[0].payload)["data"]["content"] == "<p>Open 9 to 5</p>"

import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import ApplicationScope, SchedulingApplication


class ExampleSchedulingApplication(SchedulingApplication):
    """A concrete SchedulingApplication for testing."""

    NAME = "Schedule"
    IDENTIFIER = "test_plugin__scheduling"

    def on_open(self) -> Effect | list[Effect]:
        """Forward the received provider context to the launched URL."""
        provider = self.event.context.get("provider", "")
        return [LaunchModalEffect(url=f"https://example.com/schedule?provider={provider}").apply()]


def _make_event(event_type: EventType, target: str = "", context: dict | None = None) -> Event:
    """Create an Event from the given type, target, and context."""
    return Event(EventRequest(type=event_type, target=target, context=json.dumps(context or {})))


def test_scheduling_application_scope_and_responds_to() -> None:
    """SchedulingApplication uses the scheduling scope and responds to application events."""
    assert SchedulingApplication.SCOPE == ApplicationScope.SCHEDULING
    assert EventType.Name(EventType.APPLICATION__ON_OPEN) in SchedulingApplication.RESPONDS_TO


def test_on_open_returns_launch_modal_with_context() -> None:
    """ON_OPEN delegates to on_open, which can read scheduling context from the event."""
    event = _make_event(
        EventType.APPLICATION__ON_OPEN,
        target="test_plugin__scheduling",
        context={"provider": "prov-42"},
    )
    result = ExampleSchedulingApplication(event).compute()

    assert len(result) == 1
    assert result[0].type == EffectType.LAUNCH_MODAL
    assert "provider=prov-42" in json.loads(result[0].payload)["data"]["url"]


def test_on_open_returns_empty_when_target_does_not_match() -> None:
    """ON_OPEN returns no effects when the event targets a different application."""
    event = _make_event(EventType.APPLICATION__ON_OPEN, target="wrong_identifier")
    assert ExampleSchedulingApplication(event).compute() == []

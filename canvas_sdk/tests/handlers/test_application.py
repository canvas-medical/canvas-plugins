import json

from canvas_generated.messages.effects_pb2 import Effect as EffectMessage
from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType as EventTypeEnum
from canvas_sdk.events.base import Event
from canvas_sdk.handlers.application import Application


class _FakeApp(Application):
    """A minimal concrete Application used for testing."""

    def __init__(
        self,
        event: Event,
        on_open_ret: EffectMessage | list[EffectMessage] | None = None,
        on_context_ret: EffectMessage | list[EffectMessage] | None = None,
    ) -> None:
        """Initialize the fake application with an Event and optional return values.

        Args:
            event: The Event instance to attach to the handler.
            on_open_ret: Value that will be returned from ``on_open`` when called.
            on_context_ret: Value that will be returned from ``on_context_change`` when called.
        """
        super().__init__(event)
        self._on_open_ret = on_open_ret
        self._on_context_ret = on_context_ret

    def on_open(self) -> EffectMessage | list[EffectMessage]:
        """Return the configured value for the open hook.

        Returns either a single EffectMessage, a list of EffectMessage, or None.
        """
        return self._on_open_ret or []

    def on_context_change(self) -> EffectMessage | list[EffectMessage] | None:
        """Return the configured value for the context-change hook.

        Returns either a single EffectMessage, a list of EffectMessage, or None.
        """
        return self._on_context_ret


def _make_event(event_type: EventTypeEnum, target_id: str) -> Event:
    """Create an ``Event`` wrapper from a generated EventRequest proto.

    The returned ``Event`` is the application-level wrapper used by handlers.
    """
    req = EventRequest()
    req.type = event_type
    req.target = target_id
    req.target_type = "Unknown"
    req.context = json.dumps({})
    return Event(req)


def _make_effect(type_val: EffectType) -> EffectMessage:
    """Create a lightweight EffectMessage proto for tests.

    The payload is kept empty ("{}") since the tests only assert
    normalization behavior, not payload contents.
    """
    return EffectMessage(type=type_val, payload="{}")


def test_compute_non_matching_target_returns_empty() -> None:
    """If the event target id doesn't match the application's identifier, compute returns an empty list."""
    evt = _make_event(EventTypeEnum.APPLICATION__ON_OPEN, "other-id")
    app = _FakeApp(evt, on_open_ret=_make_effect(EffectType.LAUNCH_MODAL))
    assert app.compute() == []


def test_on_open_single_and_multiple_effects() -> None:
    """Verify on_open return values are normalized to a list of effects.

    - single EffectMessage -> [EffectMessage]
    - list[EffectMessage] -> the same list
    """
    evt = _make_event(EventTypeEnum.APPLICATION__ON_OPEN, "")
    # create app and ensure identifier matches event target
    app = _FakeApp(evt, on_open_ret=_make_effect(EffectType.CALENDAR__CREATE))
    # override identifier to match
    app_id = app.identifier
    evt.target.id = app_id
    # single effect
    result = app.compute()
    assert isinstance(result, list) and len(result) == 1

    # multiple effects
    effects: list[EffectMessage] = [
        _make_effect(EffectType.CALENDAR__CREATE),
        _make_effect(EffectType.CALENDAR__EVENT__CREATE),
    ]
    app2 = _FakeApp(evt, on_open_ret=effects)
    evt.target.id = app2.identifier
    result2 = app2.compute()
    assert result2 == effects


def test_on_context_change_variants() -> None:
    """Verify on_context_change return values are normalized appropriately.

    - None -> []
    - single EffectMessage -> [EffectMessage]
    - list[EffectMessage] -> the same list
    """
    evt = _make_event(EventTypeEnum.APPLICATION__ON_CONTEXT_CHANGE, "")
    app = _FakeApp(evt, on_context_ret=None)
    evt.target.id = app.identifier
    assert app.compute() == []

    single = _make_effect(EffectType.CALENDAR__CREATE)
    app2 = _FakeApp(evt, on_context_ret=single)
    evt.target.id = app2.identifier
    res = app2.compute()
    assert isinstance(res, list) and res[0] == single

    multi = [
        _make_effect(EffectType.CALENDAR__CREATE),
        _make_effect(EffectType.CALENDAR__EVENT__CREATE),
    ]
    app3 = _FakeApp(evt, on_context_ret=multi)
    evt.target.id = app3.identifier
    res3 = app3.compute()
    assert res3 == multi

import json

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType as EventTypeEnum
from canvas_sdk.effects import Effect
from canvas_sdk.events.base import Event
from canvas_sdk.handlers.application import Application


class _FakeApp(Application):
    """Minimal concrete Application for testing normalization behavior.

    This test helper allows configuring what ``on_open`` and
    ``on_context_change`` return so we can assert that ``compute``
    normalizes those values into lists of Effect messages.
    """

    def __init__(
        self,
        event: Event,
        on_open_ret: Effect | list[Effect] | None = None,
        on_context_ret: Effect | list[Effect] | None = None,
    ) -> None:
        """Initialize with the event and optional return values for hooks.

        Args:
            event: wrapped Event instance used by handlers.
            on_open_ret: value returned by ``on_open`` when called.
            on_context_ret: value returned by ``on_context_change`` when called.
        """
        super().__init__(event)
        self._on_open_ret = on_open_ret
        self._on_context_ret = on_context_ret

    def on_open(self) -> Effect | list[Effect]:
        """Return the configured on_open value.

        May be a single Effect, an list of effects, or None.
        """
        return self._on_open_ret  # type: ignore

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Return the configured on_context_change value.

        May be a single Effect, an list of effects, or None.
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


def _make_effect(type_val: EffectType) -> Effect:
    """Create a lightweight Effect proto for tests.

    The payload is kept empty ("{}") since the tests only assert
    normalization behavior, not payload contents.
    """
    return Effect(type=type_val, payload="{}")


def test_compute_with_various_on_open_returns() -> None:
    """Ensure compute normalizes on_open return values to a list of Effects.

    This covers:
    - non-matching target (returns empty list)
    - None -> []
    - single Effect -> [Effect]
    - list[Effect] -> the same list
    - list of non-effects -> filtered out
    """
    evt = _make_event(EventTypeEnum.APPLICATION__ON_OPEN, "")

    # non-matching target -> empty list
    app = _FakeApp(evt, on_open_ret=_make_effect(EffectType.CALENDAR__CREATE))
    assert app.compute() == []

    # match identifier
    evt.target.id = _FakeApp(evt).identifier

    # None -> [] via normalize
    app_none = _FakeApp(evt, on_open_ret=None)
    assert app_none.compute() == []

    # single effect -> list
    single = _make_effect(EffectType.CALENDAR__CREATE)
    app_single = _FakeApp(evt, on_open_ret=single)
    res_single = app_single.compute()
    assert isinstance(res_single, list) and len(res_single) == 1

    # list of effects -> same list
    multi = [
        _make_effect(EffectType.CALENDAR__CREATE),
        _make_effect(EffectType.CALENDAR__EVENT__CREATE),
    ]
    app_multi = _FakeApp(evt, on_open_ret=multi)
    res_multi = app_multi.compute()
    assert res_multi == multi

    # list of non-effects -> should be filtered out by normalize_effects
    class Dummy:
        pass

    bad_iter: list = [Dummy(), Dummy()]
    app_bad = _FakeApp(evt, on_open_ret=bad_iter)
    res_bad = app_bad.compute()
    assert res_bad == []


def test_compute_with_various_on_context_change_returns() -> None:
    """Ensure compute normalizes on_context_change return values to a list of Effects.

    This covers None, single Effect, and list of Effects cases.
    """
    evt = _make_event(EventTypeEnum.APPLICATION__ON_CONTEXT_CHANGE, "")
    evt.target.id = _FakeApp(evt).identifier

    app_none = _FakeApp(evt, on_context_ret=None)
    assert app_none.compute() == []

    single = _make_effect(EffectType.CALENDAR__CREATE)
    app_single = _FakeApp(evt, on_context_ret=single)
    res_single = app_single.compute()
    assert isinstance(res_single, list) and len(res_single) == 1

    multi = [
        _make_effect(EffectType.CALENDAR__CREATE),
        _make_effect(EffectType.CALENDAR__EVENT__CREATE),
    ]
    app_multi = _FakeApp(evt, on_context_ret=multi)
    res_multi = app_multi.compute()
    assert res_multi == multi

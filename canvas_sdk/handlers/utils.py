from canvas_generated.messages.effects_pb2 import Effect as _PbEffect
from canvas_sdk.effects import Effect


def normalize_effects(effects: Effect | list[Effect] | None) -> list[Effect]:
    """Normalize effects to a list of Effect instances.

    Accepts raw ``_PbEffect`` instances too, so legacy plugins that import
    ``Effect`` directly from ``canvas_generated.messages.effects_pb2`` keep
    working through ``Application.compute()``.
    """
    if effects is None:
        return []
    if isinstance(effects, (Effect, _PbEffect)):
        return [effects]
    if isinstance(effects, list):
        return [e for e in effects if isinstance(e, (Effect, _PbEffect))]
    return []  # type: ignore[unreachable]


__exports__ = ()

from canvas_sdk.effects import Effect


def normalize_effects(effects: Effect | list[Effect] | None) -> list[Effect]:
    """Normalize effects to a list of Effect instances."""
    if effects is None:
        return []
    if isinstance(effects, Effect):
        return [effects]
    if isinstance(effects, list):
        return [e for e in effects if isinstance(e, Effect)]


__exports__ = ()

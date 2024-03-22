from typing import Any

from typing_extensions import TypedDict


class Effect(TypedDict):
    """An Effect returned from Canvas."""

    effect_type: str
    payload: dict[str, Any]

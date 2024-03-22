from typing import Any

from typing_extensions import NotRequired, TypedDict


class Coding(TypedDict):
    """Coding object in Canvas."""

    system: str
    code: str
    display: NotRequired[str]


class CommandEffectPayload(TypedDict):
    """Payload of Effect returned from a Command Class."""

    user: int
    note: NotRequired[int]
    command: NotRequired[str]
    data: NotRequired[dict[str, Any]]


class CommandEffect(TypedDict):
    """Effect returned from a Command Class."""

    effect_type: str
    payload: CommandEffectPayload

from typing_extensions import NotRequired, TypedDict


class Coding(TypedDict):
    """Coding object in Canvas."""

    system: str
    code: str
    display: NotRequired[str]

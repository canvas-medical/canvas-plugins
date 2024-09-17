from pydantic import BaseModel, ConfigDict
from typing_extensions import Literal, NotRequired, TypedDict

from canvas_sdk.commands.constants import Coding


class Recommendation(BaseModel):
    """
    A Recommendation for a Protocol Card.
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    class Command(TypedDict):
        type: str
        filter: NotRequired[dict[Literal["coding"], list[Coding]]]

    title: str = ""
    button: str = ""
    href: str | None = None
    command: Command | None = None
    context: dict | None = None

from pydantic import BaseModel, ConfigDict
from typing_extensions import Literal, NotRequired, TypedDict


class Recommendation(BaseModel):
    """
    A Recommendation for a Protocol Card.
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    class CodingFilter(TypedDict):
        system: Literal["cpt", "cvx", "snomedct", "rxnorm", "loinc", "icd10cm", "fdb", "ndc"]
        code: str

    class Command(TypedDict):
        type: str
        filter: NotRequired[dict[Literal["coding"], list[CodingFilter]]]

    title: str = ""
    button: str = ""
    href: str | None = None
    command: Command | None = None
    context: dict | None = None

from typing_extensions import Literal, NotRequired, TypedDict


class RecommendationCodingFilter(TypedDict):
    """A coding object intended for use in a ProtocolCard Recommendation filter."""

    system: Literal["cpt", "cvx", "snomedct", "rxnorm", "loinc", "icd10cm", "fdb", "ndc"]
    code: str


class RecommendationCommand(TypedDict):
    """A command object intended for use in a ProtocolCard Recommendation."""

    type: str
    filter: NotRequired[dict[Literal["coding"], list[RecommendationCodingFilter]]]

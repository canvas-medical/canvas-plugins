from pydantic import BaseModel, ConfigDict

from canvas_sdk.effects.protocol_card.constants import RecommendationCommand


class Recommendation(BaseModel):
    """
    A Recommendation for a Protocol Card.
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    title: str = ""
    button: str = ""
    href: str | None = None
    command: RecommendationCommand | None = None
    context: dict | None = None

from enum import Enum
from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.effects.protocol_card.recommendation import Recommendation


class ProtocolCard(_BaseEffect):
    """
    An Effect that will result in a protocol card in Canvas.
    """

    class Status(Enum):
        DUE = "due"
        SATISFIED = "satisfied"

    class Meta:
        effect_type = EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

    patient_id: str
    key: str
    title: str = ""
    narrative: str = ""
    recommendations: list[Recommendation] = []
    status: Status = Status.DUE  # type: ignore

    @property
    def values(self) -> dict[str, Any]:
        """The ProtocolCard's values."""
        return {
            "title": self.title,
            "narrative": self.narrative,
            "recommendations": self.recommendations,
            "status": self.status,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"patient": self.patient_id, "key": self.key, "data": self.values}

    def add_recommendation(
        self,
        title: str = "",
        button: str = "",
        href: str | None = None,
        command: Recommendation.Command | None = None,
        context: dict | None = None,
    ) -> None:
        """Adds a recommendation to the protocol card's list of recommendations."""
        recommendation = Recommendation(
            title=title, button=button, href=href, command=command, context=context
        )
        self.recommendations.append(recommendation)

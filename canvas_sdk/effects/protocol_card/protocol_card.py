from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from canvas_sdk.effects.base import EffectType, _BaseEffect


class Recommendation(BaseModel):
    """
    A Recommendation for a Protocol Card.
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    title: str = ""
    button: str = ""
    href: str | None = None
    command: str | None = None
    context: dict | None = None

    @property
    def values(self) -> dict:
        """The ProtocolCard recommendation's values."""
        return {
            "title": self.title,
            "button": self.button,
            "href": self.href,
            "command": {"type": self.command} if self.command else {},
            "context": self.context or {},
        }


class ProtocolCard(_BaseEffect):
    """
    An Effect that will result in a protocol card in Canvas.
    """

    class Status(Enum):
        DUE = "due"
        SATISFIED = "satisfied"
        NOT_APPLICABLE = "not_applicable"
        PENDING = "pending"
        NOT_RELEVANT = "not_relevant"

    class Meta:
        effect_type = EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
        apply_required_fields = ("patient_id|patient_filter", "key")

    patient_id: str | None = None
    key: str | None = None
    title: str = ""
    narrative: str = ""
    recommendations: list[Recommendation] = []
    status: Status = Status.DUE
    feedback_enabled: bool = False
    due_in: int = -1

    @property
    def values(self) -> dict[str, Any]:
        """The ProtocolCard's values."""
        return {
            "title": self.title,
            "narrative": self.narrative,
            "recommendations": [
                rec.values | {"key": i} for i, rec in enumerate(self.recommendations)
            ],
            "status": self.status.value,
            "feedback_enabled": self.feedback_enabled,
            "due_in": self.due_in,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {
            "patient": self.patient_id,
            "patient_filter": self.patient_filter,
            "key": self.key,
            "data": self.values,
        }

    def add_recommendation(
        self,
        title: str = "",
        button: str = "",
        href: str | None = None,
        command: str | None = None,
        context: dict | None = None,
    ) -> None:
        """Adds a recommendation to the protocol card's list of recommendations."""
        recommendation = Recommendation(
            title=title, button=button, href=href, command=command, context=context
        )
        self.recommendations.append(recommendation)


__exports__ = (
    "Recommendation",
    "ProtocolCard",
)

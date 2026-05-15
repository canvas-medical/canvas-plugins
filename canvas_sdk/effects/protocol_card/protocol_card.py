from enum import Enum
from typing import Any, overload

from pydantic import BaseModel, ConfigDict, field_validator

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.effects.base import EffectType, _BaseEffect


class Recommendation(BaseModel):
    """
    A Recommendation for a Protocol Card.
    """

    model_config = ConfigDict(strict=True, validate_assignment=True)

    title: str = ""
    button: str = ""
    href: str | None = None
    commands: list[Any] | None = None

    @field_validator("commands", mode="before")
    @classmethod
    def check_subclass(cls, commands: list[Any] | None) -> list[Any] | None:
        """Validates that all commands are subclasses of _BaseCommand or dicts."""
        if commands is None:
            return commands
        for command in commands:
            if not isinstance(command, (_BaseCommand, dict)):
                raise TypeError(f"'{type(command)}' must be subclass of _BaseCommand")
        return commands

    @property
    def values(self) -> dict:
        """The ProtocolCard recommendation's values."""
        return {
            "title": self.title,
            "button": self.button,
            "href": self.href,
            "commands": [
                command.recommendation_context() if isinstance(command, _BaseCommand) else command
                for command in self.commands
            ]
            if self.commands
            else [],
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
    can_be_snoozed: bool = False

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
            "can_be_snoozed": self.can_be_snoozed,
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

    @overload
    def add_recommendation(
        self,
        title: str = "",
        button: str = "",
        href: str | None = None,
        command: str | None = None,
        context: dict | None = None,
    ) -> None: ...

    @overload
    def add_recommendation(
        self,
        title: str = "",
        button: str = "",
        href: str | None = None,
        commands: list[Any] | None = None,
    ) -> None: ...

    def add_recommendation(  # type: ignore[misc]
        self,
        title: str = "",
        button: str = "",
        href: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Adds a recommendation to the protocol card's list of recommendations."""
        if "commands" in kwargs and "command" in kwargs:
            raise ValueError("Cannot provide both 'commands' and 'command'")

        commands: list[Any] = []
        if "command" in kwargs:
            command = kwargs.pop("command")
            context = kwargs.pop("context", {}) or {}
            if command:
                commands.append({"command": {"type": command}, "context": context})
        elif "commands" in kwargs:
            commands = kwargs.pop("commands") or []

        recommendation = Recommendation(
            title=title,
            button=button,
            href=href,
            commands=commands,
        )
        self.recommendations.append(recommendation)


__exports__ = (
    "Recommendation",
    "ProtocolCard",
)

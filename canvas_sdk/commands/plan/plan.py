from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.plan.schema import PlanCommandSchema


class PlanCommand(_BaseCommand):
    """A class for managing a Plan command within a specific note."""

    schema = PlanCommandSchema

    narrative: str | None

    def __init__(
        self,
        user_id: int | None = None,
        note_id: int | None = None,
        command_uuid: str | None = None,
        narrative: str | None = None,
    ) -> None:
        super().__init__(user_id=user_id, note_id=note_id, command_uuid=command_uuid)
        self.narrative = narrative

    @property
    def values(self) -> dict:
        """The Plan command's field values."""
        return {"narrative": self.narrative}

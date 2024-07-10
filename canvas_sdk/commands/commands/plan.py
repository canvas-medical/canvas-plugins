from canvas_sdk.commands.base import _BaseCommand


class PlanCommand(_BaseCommand):
    """A class for managing a Plan command within a specific note."""

    class Meta:
        key = "plan"
        originate_required_fields = ("narrative",)

    narrative: str | None = None

    @property
    def values(self) -> dict:
        """The Plan command's field values."""
        return {"narrative": self.narrative}

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class PerformCommand(BaseCommand):
    """A class for managing a Perform command within a specific note."""

    class Meta:
        key = "perform"
        commit_required_fields = ("cpt_code",)

    cpt_code: str
    notes: str | None = None

    @property
    def values(self) -> dict:
        """The Perform command's field values."""
        return {"cpt_code": self.cpt_code, "notes": self.notes}

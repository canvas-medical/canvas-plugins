from canvas_sdk.commands.base import _BaseCommand


class HistoryOfPresentIllnessCommand(_BaseCommand):
    """A class for managing a HPI command within a specific note."""

    class Meta:
        key = "hpi"
        commit_required_fields = ("narrative",)

    narrative: str | None = None

    @property
    def values(self) -> dict:
        """The HPI command's field values."""
        return {"narrative": self.narrative}

from canvas_sdk.commands.commands.base import _BaseCommand


class HistoryOfPresentIllnessCommand(_BaseCommand):
    """A class for managing a HPI command within a specific note."""

    narrative: str

    @property
    def values(self) -> dict:
        """The HPI command's field values."""
        return {"narrative": self.narrative}
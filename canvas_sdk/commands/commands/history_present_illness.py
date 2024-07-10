from canvas_sdk.commands.base import _BaseCommand


class HistoryOfPresentIllnessCommand(_BaseCommand):
    """A class for managing a HPI command within a specific note."""

    class Meta:
        key = "hpi"

    narrative: str

    @property
    def values(self) -> dict:
        """The HPI command's field values."""
        return {"narrative": self.narrative}


class HistoryOfPresentIllnessCommandNoInitValidation:
    """HPI Command without validation on initialization."""

    def __new__(cls, **kwargs: dict) -> HistoryOfPresentIllnessCommand:
        """Returns an initialized HPI Command without any validation."""
        return HistoryOfPresentIllnessCommand.model_construct(**kwargs)

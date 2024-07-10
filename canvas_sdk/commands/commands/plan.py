from canvas_sdk.commands.base import _BaseCommand


class PlanCommand(_BaseCommand):
    """A class for managing a Plan command within a specific note."""

    class Meta:
        key = "plan"

    narrative: str

    @property
    def values(self) -> dict:
        """The Plan command's field values."""
        return {"narrative": self.narrative}


class PlanCommandNoInitValidation:
    """Plan Command without validation on initialization."""

    def __new__(cls, **kwargs: dict) -> PlanCommand:
        """Returns an initialized Plan Command without any validation."""
        return PlanCommand.model_construct(**kwargs)

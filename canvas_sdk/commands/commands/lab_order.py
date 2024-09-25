from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class LabOrderCommand(BaseCommand):
    """A class for managing a Lab Order command within a specific note."""

    class Meta:
        key = "labOrder"
        commit_required_fields = (
            "lab_partner",
            "tests_order_codes",
            "ordering_provider",
            "diagnosis_codes",
        )

    lab_partner: str | None = None
    tests_order_codes: list[str] = []
    ordering_provider_key: str | None = None
    diagnosis_codes: list[str] = []
    fasting_required: bool = False
    comment: str | None = None

    @property
    def values(self) -> dict:
        """The Lab Order command's field values."""
        return {
            "lab_partner": self.lab_partner,
            "tests_order_codes": self.tests_order_codes,
            "ordering_provider_key": self.ordering_provider_key,
            "diagnosis_codes": self.diagnosis_codes,
            "fasting_required": self.fasting_required,
            "comment": self.comment,
        }

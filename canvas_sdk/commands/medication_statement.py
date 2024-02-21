from canvas_sdk.commands.base import _BaseCommand


class MedicationStatementCommand(_BaseCommand):
    """A class for managing a MedicationStatement command within a specific note."""

    fdb_code: str
    sig: str | None = None

    @property
    def values(self) -> dict:
        """The MedicationStatement command's field values."""
        return {"fdb_code": self.fdb_code, "sig": self.sig}

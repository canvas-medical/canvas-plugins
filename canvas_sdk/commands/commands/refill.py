from canvas_sdk.commands.commands.prescribe import PrescribeCommand


class RefillCommand(PrescribeCommand):
    """A class for managing a Refill command within a specific note."""

    class Meta:
        key = "refill"
        commit_required_fields = (
            "fdb_code",
            "sig",
            "quantity_to_dispense",
            "type_to_dispense",
            "refills",
            "substitutions",
            "prescriber_id",
        )

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class FamilyHistoryCommand(BaseCommand):
    """A class for managing a Family History command within a specific note."""

    class Meta:
        key = "familyHistory"
        commit_required_fields = ("family_history",)

    family_history: str | None = None
    relative: str | None = None
    note: str | None = None

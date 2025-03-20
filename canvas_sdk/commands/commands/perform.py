from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class PerformCommand(BaseCommand):
    """A class for managing a Perform command within a specific note."""

    class Meta:
        key = "perform"
        commit_required_fields = ("cpt_code",)

    cpt_code: str | None = None
    notes: str | None = None

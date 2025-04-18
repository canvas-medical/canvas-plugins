from canvas_sdk.commands.base import _BaseCommand


class PlanCommand(_BaseCommand):
    """A class for managing a Plan command within a specific note."""

    class Meta:
        key = "plan"
        commit_required_fields = ("narrative",)

    narrative: str = ""

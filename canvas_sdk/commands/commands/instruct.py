from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class InstructCommand(BaseCommand):
    """A class for managing an Instruct command within a specific note."""

    class Meta:
        key = "instruct"
        commit_required_fields = ("instruction",)

    instruction: str | None = None
    comment: str | None = None

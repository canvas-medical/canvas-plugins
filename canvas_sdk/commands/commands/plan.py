from canvas_sdk.commands.commands.assessment_link import _AssessmentLinkedCommand


class PlanCommand(_AssessmentLinkedCommand):
    """A class for managing a Plan command within a specific note."""

    class Meta:
        key = "plan"

    narrative: str = ""


__exports__ = ("PlanCommand",)

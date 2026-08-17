from canvas_sdk.commands.commands.plan import PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.note_body_automation import NoteBodyAutomation
from canvas_sdk.v1.data.note import NoteTypeCategories


class PatientSummaryAutomation(NoteBodyAutomation):
    """An automation that opens a modal with a patient summary."""

    AUTOMATION_KEY = "patient_summary"
    AUTOMATION_TITLE = "Patient summary"
    KEYWORDS = ["summary", "overview", "recap"]
    PRIORITY = 1

    def handle(self) -> list[Effect]:
        """Open the summary in the right chart pane."""
        return [
            LaunchModalEffect(
                content="<h1>Patient summary</h1><p>Your summary goes here.</p>",
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                title="Patient summary",
            ).apply()
        ]


class FollowUpPlanAutomation(NoteBodyAutomation):
    """An automation that adds a Plan command with a follow-up narrative.

    Canvas puts the command on the line that the user typed on. Do not give
    ``originate`` a ``line_number``.
    """

    AUTOMATION_KEY = "follow_up_plan"
    AUTOMATION_TITLE = "Follow-up plan"
    KEYWORDS = ["follow", "followup", "plan"]
    PRIORITY = 2

    def visible(self) -> bool:
        """Show this automation in office visit notes only."""
        note = self.note
        if not note:
            return False
        return note.note_type_version.category == NoteTypeCategories.ENCOUNTER

    def handle(self) -> list[Effect]:
        """Add the Plan command to the note."""
        note = self.note
        if not note:
            return []
        return [
            PlanCommand(
                note_uuid=str(note.id),
                narrative="Follow up in 2 weeks.",
            ).originate()
        ]

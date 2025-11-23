from canvas_sdk.commands import PrescribeCommand
from canvas_sdk.effects import Effect
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.v1.data import Command


class SendPrescriptionButtonHandler(ActionButton):
    """Button handler for sending all prescriptions from a note."""

    BUTTON_TITLE = "Send Prescriptions"
    BUTTON_KEY = "SEND_ALL_PRESCRIPTIONS"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_FOOTER

    def handle(self) -> list[Effect]:
        """Handle sending all prescriptions from the current note."""
        note_id = self.context.get("note_id")

        effects: list[Effect] = []
        # get all committed prescribe commands
        prescribe_commands = Command.objects.filter(
            note_id=note_id, schema_key="prescribe", committer__isnull=False
        )

        for command in prescribe_commands:
            prescribe = PrescribeCommand()
            prescribe.command_uuid = str(command.id)
            effects.append(prescribe.send())

        return effects

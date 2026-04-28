from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class GlobalApp(Application):
    """A global companion application not tied to any patient or note.

    Global companion apps appear on the companion main page and are suitable
    for workflows that span multiple patients or are administrative in nature,
    such as a schedule viewer, task list, or inter-office chat.
    """

    def on_open(self) -> Effect:
        """Handle the on_open event for a global companion app."""
        return LaunchModalEffect(
            url="/plugin-io/api/example_provider_companion_app/app/global",
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        ).apply()


class PatientApp(Application):
    """A patient-specific companion application.

    Patient-specific companion apps appear on the patient detail page and
    receive the patient's ID in the event context. They are suitable for
    workflows that operate on a single patient, such as a vitals visualizer,
    chart summary, or risk scoring tool.
    """

    def on_open(self) -> Effect:
        """Handle the on_open event for a patient-specific companion app.

        The patient's key is available in self.event.context["patient"]["id"].
        """
        patient = self.event.context.get("patient", {})
        patient_id = patient.get("id", "")

        return LaunchModalEffect(
            url=f"/plugin-io/api/example_provider_companion_app/app/patient?patient_id={patient_id}",
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        ).apply()


class NoteApp(Application):
    """A note-specific companion application.

    Note-specific companion apps appear within an expanded note on the patient
    detail page. They receive both patient and note information in the event
    context. They are suitable for workflows that operate on a single encounter,
    such as a documentation assistant or coding tool.
    """

    def on_open(self) -> Effect:
        """Handle the on_open event for a note-specific companion app.

        The patient's key is available in self.event.context["patient"]["id"].
        The note's UUID is available in self.event.context["note"]["id"].
        """
        patient = self.event.context.get("patient", {})
        patient_id = patient.get("id", "")
        note = self.event.context.get("note", {})
        note_id = note.get("id", "")

        return LaunchModalEffect(
            url=(
                f"/plugin-io/api/example_provider_companion_app/app/note"
                f"?patient_id={patient_id}&note_id={note_id}"
            ),
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        ).apply()

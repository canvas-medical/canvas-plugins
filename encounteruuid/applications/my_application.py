import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.v1.data import Patient, Encounter


class MyApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        data = {}
        patient = Patient.objects.get(id=self.event.context["patient"]["id"])
        for note in patient.notes.filter(encounter__isnull=False):
            key = f"note{note.dbid}"
            encounter = note.encounter
            data[key] = {
                "id": str(note.dbid),
                "uuid": str(note.id),
                "encounter_id": str(encounter.dbid) if encounter else None,
                "encounter": {
                    "uuid": str(encounter.id),
                    "created": str(encounter.created),
                    "modified": str(encounter.modified),
                    "medium": str(encounter.medium),
                    "state": str(encounter.state),
                    "start_time": str(encounter.start_time),
                    "end_time": str(encounter.end_time),
                }
                if encounter
                else None,
                "created": str(note.created),
                "modified": str(note.modified),
                "patient_id": str(note.patient_id),
                "patient": {"first_name": note.patient.first_name},
                "provider_id": str(note.provider_id),
                "provider": {"first_name": note.provider.first_name},
                "note_type": str(note.note_type),
                "note_type_version": str(note.note_type_version),
                "title": str(note.title),
                "body": str(note.body),
                "originator_id": str(note.originator_id),
                "originator": {"email": note.originator.email},
                "last_modified_by_staff_id": str(note.last_modified_by_staff_id),
                "last_modified_by_staff": {"email": note.last_modified_by_staff.email},
                "checksum": str(note.checksum),
                "billing_note": str(note.billing_note),
                "related_data": str(note.related_data),
                "location": str(note.location),
                "datetime_of_service": str(note.datetime_of_service),
                "place_of_service": str(note.place_of_service),
            }

        return LaunchModalEffect(
            content=f"""<pre id="json-output">{json.dumps(data, indent=4)}</pre>""",
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
        ).apply()

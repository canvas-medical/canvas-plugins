from http import HTTPStatus

import arrow
from django.db.models import Count, Q, F

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import Response, JSONResponse
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import StaffSessionAuthMixin, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Note, Command, Referral, ImagingOrder
from canvas_sdk.v1.data.note import NoteStates
from canvas_sdk.v1.data.task import TaskStatus
from logger import log


class MyApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        """Handle the on_open event."""
        return LaunchModalEffect(
            content=render_to_string("templates/encounter_list.html"),
            target=LaunchModalEffect.TargetType.PAGE,
        ).apply()


class EncounterListApi(StaffSessionAuthMixin, SimpleAPI):
    """API for encounter list functionality."""

    @api.get("/encounters")
    def get_encounters(self) -> list[Response | Effect]:
        """Get list of open encounters."""
        provider_id = self.request.query_params.get("provider_id")
        location_id = self.request.query_params.get("location_id")
        billable_only = self.request.query_params.get("billable_only") == "true"

        note_queryset = Note.objects.filter(current_state__state__in=(NoteStates.NEW, NoteStates.UNLOCKED))

        if provider_id:
            note_queryset = note_queryset.filter(provider__id=provider_id)

        if location_id:
            note_queryset = note_queryset.filter(location__id=location_id)

        # Add annotations
        note_queryset = note_queryset.annotate(
            staged_commands_count=Count(
                'commands',
                filter=Q(commands__state__in=('staged', 'in_review',))
            ),
            is_billable=F('note_type_version__is_billable'),
        )

        if billable_only:
            note_queryset = note_queryset.filter(is_billable=True)

        # Convert queryset to encounter data
        encounters = []
        for note in note_queryset:
            claim_queue = note.get_claim().current_queue.name if note.get_claim() else None

            delegated_commands = 0
            # Fetch commands that can be delegated related to the note
            delegatable_commands = Command.objects.filter(note=note, schema_key__in=("imagingOrder", "refer",))
            for command in delegatable_commands:
                # Get the anchor object for the command
                anchor_object = command.anchor_object
                if not anchor_object:
                    continue

                should_increase = False
                # If the command is delegated increment the count
                if isinstance(anchor_object, Referral) and anchor_object.forwarded:
                    should_increase = True
                elif isinstance(anchor_object, ImagingOrder) and anchor_object.delegated:
                    should_increase = True

                if should_increase and anchor_object.get_task_objects().filter(status=TaskStatus.OPEN).exists():
                    delegated_commands = delegated_commands + 1

            encounter_data = {
                "id": str(note.id),
                "dbid": note.dbid,
                "patient_name": note.patient.preferred_full_name if note.patient else "Unknown Patient",
                "patient_id": str(note.patient.id) if note.patient else None,
                "patient_dob": arrow.get(note.patient.birth_date).format(
                    "MMM DD, YYYY") if note.patient and note.patient.birth_date else "Unknown",
                "provider": note.provider.credentialed_name if note.provider else "Unknown Provider",
                "provider_id": str(note.provider.id) if note.provider else None,
                "note_title": note.note_type_version.name or "Untitled Note",
                "dos": arrow.get(note.datetime_of_service).format(
                    "MMM DD, YYYY") if note.datetime_of_service else "Unknown",
                "dos_iso": note.datetime_of_service.isoformat() if note.datetime_of_service else None,
                "billable": note.is_billable,
                "uncommitted_commands": note.staged_commands_count,
                "delegated_orders": delegated_commands,
                "claim_queue": claim_queue,
                "location": note.location.full_name if note.location else "Unknown Location",
                "location_id": str(note.location.id) if note.location else None,
                "created": note.created.isoformat() if note.created else None,
            }
            encounters.append(encounter_data)

        return [JSONResponse({
            "encounters": encounters,
            "total_count": len(encounters)
        }, status_code=HTTPStatus.OK)]

    @api.get("/providers")
    def get_providers(self) -> list[Response | Effect]:
        """Get list of providers who have notes."""

        providers = [{"id": n.provider.id, "name": n.provider.credentialed_name}
                     for n in
                     Note.objects.filter(current_state__state__in=(NoteStates.NEW, NoteStates.UNLOCKED)).distinct(
                         "provider__id")]

        return [JSONResponse({
            "providers": providers
        }, status_code=HTTPStatus.OK)]

    @api.get("/locations")
    def get_locations(self) -> list[Response | Effect]:
        """Get list of practice locations that have notes."""

        locations = [{"id": str(n.location.id), "name": n.location.full_name}
                     for n in
                     Note.objects.filter(current_state__state__in=(NoteStates.NEW, NoteStates.UNLOCKED))
                     .filter(location__isnull=False)
                     .distinct("location__id")]

        return [JSONResponse({
            "locations": locations
        }, status_code=HTTPStatus.OK)]

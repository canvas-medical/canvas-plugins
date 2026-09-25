from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api
from canvas_sdk.handlers.simple_api.security import StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.note import Note
from note_custom_content.sections import (
    ADD_LABELS,
    ADDS,
    LABELS,
    channel_for,
    counts_for,
    section_for,
)


class NoteContentAPI(StaffSessionAuthMixin, SimpleAPI):
    """Serves the note's blocks, and adds the command a section's button offers.

    The blocks are served from here rather than inlined into the effect so each one is a
    real page: it has its own origin and its own devtools, and its socket survives Canvas
    re-rendering the frame around it.
    """

    @api.get("/banner")
    def banner(self) -> list[Response | Effect]:
        """The summary that reads above the note body."""
        note_id = self.request.query_params.get("note_id", "")
        note = Note.objects.select_related("patient", "provider").filter(id=note_id).first()

        if not note:
            return [Response(b"Not found", status_code=HTTPStatus.NOT_FOUND)]

        return [
            HTMLResponse(
                render_to_string(
                    "templates/note_banner.html",
                    {
                        "patient_name": f"{note.patient.first_name} {note.patient.last_name}",
                        "birth_date": note.patient.birth_date,
                        "sex_at_birth": note.patient.sex_at_birth,
                        "provider_name": (
                            f"{note.provider.first_name} {note.provider.last_name}"
                            if note.provider
                            else "Unassigned"
                        ),
                        "date_of_service": note.datetime_of_service,
                        "total": counts_for(note_id)["total"],
                        "channel": channel_for(note_id),
                    },
                )
            )
        ]

    @api.get("/section")
    def section(self) -> list[Response | Effect]:
        """The card that reads inside one section of the note."""
        note_id = self.request.query_params.get("note_id", "")
        section = section_for(self.request.query_params.get("section", ""))

        if not note_id or section is None:
            return [Response(b"Not found", status_code=HTTPStatus.NOT_FOUND)]

        return [
            HTMLResponse(
                render_to_string(
                    "templates/section_card.html",
                    {
                        "label": LABELS[section],
                        "count": counts_for(note_id)[section.value],
                        "add_label": ADD_LABELS.get(section),
                        "section": section.value,
                        "note_id": note_id,
                        "channel": channel_for(note_id),
                    },
                )
            )
        ]

    @api.post("/originate")
    def originate(self) -> list[Response | Effect]:
        """Add the command the named section's button offers."""
        payload = self.request.json()
        note_id = payload.get("note_id")
        section = section_for(payload.get("section", ""))

        if not note_id or section is None or section not in ADDS:
            return [
                JSONResponse(
                    {"error": "a note and a section this plugin can add to are both required"},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

        return [
            ADDS[section](note_uuid=note_id).originate(),
            JSONResponse({"added": ADDS[section].Meta.key}),
        ]

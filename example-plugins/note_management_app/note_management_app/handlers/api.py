from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Note as NoteModel


class AppApi(SimpleAPI):
    """API handler for serving the note management application."""

    PREFIX = ""

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow access to the application without authentication.
        The OAuth flow will handle authentication within the app.
        """
        return True

    @api.get("/app")
    def note_management_app(self) -> list[Response | Effect]:
        """Serve the note management application HTML."""
        # Get the Canvas instance URL from the request Host header
        host = self.request.headers.get("Host", "localhost:8000")

        # Determine protocol based on host
        if "localhost" in host or "127.0.0.1" in host:
            canvas_instance = f"http://{host}"
        else:
            canvas_instance = f"https://{host}"

        # Render the HTML template with context
        context = {"canvas_instance": canvas_instance, "client_id": self.secrets.get("client_id")}

        return [
            HTMLResponse(
                render_to_string("templates/note_management_app.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/notes/recent")
    def get_recent_notes(self) -> list[Response | Effect]:
        """Get the 10 most recent notes with patient info and status."""
        # Fetch the 10 most recent notes
        notes = NoteModel.objects.select_related(
            "patient", "note_type_version", "current_state"
        ).order_by("-created")[:10]

        notes_data = []
        for note in notes:
            # Get the display state name instead of the state code
            current_state = note.current_state
            display_state = current_state.get_state_display() if current_state else "Unknown"

            notes_data.append(
                {
                    "id": str(note.id),
                    "patient_name": f"{note.patient.first_name} {note.patient.last_name}"
                    if note.patient
                    else "Unknown",
                    "current_state": display_state,
                    "is_sig_required": note.note_type_version.is_sig_required
                    if note.note_type_version
                    else False,
                    "created": note.created.isoformat() if note.created else None,
                }
            )

        return [JSONResponse({"notes": notes_data}, status_code=HTTPStatus.OK)]


class NoteApi(SimpleAPI):
    """API handler for note-related operations."""

    PREFIX = "/notes"

    def authenticate(self, credentials: Credentials) -> bool:
        """Change this method to authenticate based on your needs.
        More info at: https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#authentication.
        """
        return self.event.actor.instance is not None

    @api.post("/<id>/lock")
    def lock_note(self) -> list[Response | Effect]:
        """Lock a note."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            note_instance = None

        if not note_instance:
            return [
                JSONResponse(
                    {
                        "error": "Note not found.",
                        "body": self.request.text(),
                        "headers": dict(self.request.headers),
                    },
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        note = Note(instance_id=note_instance.id)

        return [note.lock()]

    @api.post("/<id>/sign")
    def sign_note(self) -> list[Response | Effect]:
        """Sign a note."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            note_instance = None

        if not note_instance:
            return [
                JSONResponse(
                    {
                        "error": "Note not found.",
                        "body": self.request.text(),
                        "headers": dict(self.request.headers),
                    },
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        note = Note(instance_id=note_instance.id)
        if note_instance.note_type_version.is_sig_required:
            return [note.sign()]
        else:
            return []

    @api.post("/<id>/lock_sign")
    def lock_and_sign_note(self) -> list[Response | Effect]:
        """Lock/sign a note."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            note_instance = None

        if not note_instance:
            return [
                JSONResponse(
                    {
                        "error": "Note not found.",
                        "body": self.request.text(),
                        "headers": dict(self.request.headers),
                    },
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        note = Note(instance_id=note_instance.id)
        # if signature is required for the note, lock and sign it, otherwise just lock it
        if note_instance.note_type_version.is_sig_required:
            return [note.lock(), note.sign()]
        else:
            return [note.lock()]

    @api.post("/<id>/unlock")
    def unlock_note(self) -> list[Response | Effect]:
        """Unlock a note."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            note_instance = None

        if not note_instance:
            return [
                JSONResponse(
                    {"error": "Note not found."},
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        note = Note(instance_id=note_instance.id)

        return [note.unlock()]

    @api.post("/<id>/checkin")
    def check_in_note(self) -> list[Effect | Response]:
        """Check in a note."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            note_instance = None

        if not note_instance:
            return [
                JSONResponse(
                    {"error": "Note not found."},
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        note = Note(instance_id=note_instance.id)
        try:
            return [note.check_in()]
        except Exception as e:
            return [
                JSONResponse(
                    {"error": str(e)},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

    @api.post("/<id>/noshow")
    def noshow_note(self) -> list[Effect | Response]:
        """Mark a note as no-show."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            note_instance = None

        if not note_instance:
            return [
                JSONResponse(
                    {"error": "Note not found."},
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        note = Note(instance_id=note_instance.id)
        try:
            return [note.no_show()]
        except Exception as e:
            return [
                JSONResponse(
                    {"error": str(e)},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

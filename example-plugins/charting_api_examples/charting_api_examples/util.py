from http import HTTPStatus
from uuid import UUID

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.v1.data.note import Note


def is_valid_uuid(possible_uuid: str) -> bool:
    """Check if a string is a valid UUID version 4."""
    try:
        uuid_obj = UUID(possible_uuid, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == possible_uuid


def note_not_found_response() -> JSONResponse:
    """Return a standardized 404 response for notes not found."""
    return JSONResponse(
        {"error": "Note not found."},
        status_code=HTTPStatus.NOT_FOUND,
    )


def get_note_from_path_params(path_params: dict[str, str]) -> Note | None:
    """Extract and validate note from path parameters."""
    note_id = path_params["id"]
    # Ensure the note id is a valid UUID
    if not is_valid_uuid(note_id):
        return None

    try:
        note = Note.objects.get(id=note_id)
    except Note.DoesNotExist:
        return None
    return note

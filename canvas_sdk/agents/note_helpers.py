"""SDK helpers for tools that need to act on a patient's current note.

The canonical "find the patient's open note" lookup, plus a
ready-made :func:`find_open_note_uuid_from_ctx` resolver compatible
with :meth:`ToolRegistry.originate_command_tool`'s ``note_resolver``
parameter.

Use this from chat-style agents and other user-initiated tools that
don't have an inbound ``note_id`` on ``trigger_payload`` but still
need to land a draft command on whatever note the clinician has open.
For agents triggered on a specific note, prefer the default resolver
that just reads ``ctx["note_id"]``.
"""

from typing import Any

from canvas_sdk.v1.data import Note
from canvas_sdk.v1.data.note import NoteStates

# Notes in any of these states accept new originated commands. Locked /
# signed / deleted / etc. notes are immutable to clinical-integrity
# validation, so we exclude them — staging a command on one would fail
# `canvas_core.commands.utils._validate_note` at ingest time.
OPEN_NOTE_STATES = (
    NoteStates.NEW,
    NoteStates.UNLOCKED,
    NoteStates.CONVERTED,
)


def find_open_note(patient_id: str) -> Note | None:
    """Return the patient's most-recent mutable note, or ``None``.

    "Open" here means the note is in a state that accepts new originated
    commands (see :data:`OPEN_NOTE_STATES`). Ordered by
    ``datetime_of_service`` descending so the clinician's currently-
    active encounter wins over older drafts.

    Args:
        patient_id: The patient's UUID (the canonical ``Patient.id``,
            not the integer ``dbid``).

    Returns:
        The :class:`Note` instance, or ``None`` if the patient has no
        notes in an open state.
    """
    return (
        Note.objects.filter(
            patient__id=patient_id,
            current_state__state__in=OPEN_NOTE_STATES,
        )
        .order_by("-datetime_of_service")
        .first()
    )


def find_open_note_uuid_from_ctx(ctx: dict[str, Any]) -> str | None:
    """``note_resolver`` for tools that originate on the patient's current open note.

    Drop-in for :meth:`ToolRegistry.originate_command_tool`'s
    ``note_resolver`` parameter when the agent isn't bound to a specific
    note (chat-style and user-action surfaces). Falls back to ``None`` if
    no open note exists — the helper translates that into a structured
    error returned to the model.

    Reads ``patient_id`` from ``ctx``; the agent is responsible for
    populating it before invoking tools.
    """
    patient_id = ctx.get("patient_id")
    if not patient_id:
        return None
    note = find_open_note(patient_id)
    return str(note.id) if note is not None else None


__exports__ = (
    "OPEN_NOTE_STATES",
    "find_open_note",
    "find_open_note_uuid_from_ctx",
)

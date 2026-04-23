"""
Note access restriction handlers.

This module implements the ``NoteRestrictionsEffect`` use-cases described in KOALA-4025:

* **Concurrent edit locking** — when a note's body changes, a time-limited edit lock is
  written to ``NoteMetadata``.  Other users see a banner and cannot edit the note until the
  lock expires (``RESTRICTION_EXPIRY_MINUTES``) or is released.

* **Role-based access restriction** — certain note types (e.g. "Office visit") are
  restricted to a designated staff member.  All other users see a blur and an access-denied
  banner.

Both mechanisms respond to ``GET_NOTE_RESTRICTIONS`` with a ``NoteRestrictionsEffect``, and
broadcast a ``NoteRestrictionsUpdatedEffect`` so connected clients refetch permissions in
real time.
"""

import json
from uuid import UUID

import arrow

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note as NoteEffect
from canvas_sdk.effects.note.restrictions import (
    NoteRestrictionsEffect,
    NoteRestrictionsUpdatedEffect,
)
from canvas_sdk.effects.patient.timeline import PatientTimelineEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.handlers.cron_task import CronTask
from canvas_sdk.v1.data import NoteMetadata, NoteType
from canvas_sdk.v1.data.letter import Letter
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.staff import Staff
from note_timeline_restrictions.models.config import (
    NoteTypeAccessConfig,  # CustomModel — table created via custom_data manifest entry
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# NoteMetadata key used to store the active edit lock for a note.
RESTRICTION_KEY = "restriction"

# Namespaced key for the persisted body checksum used to detect concurrent edits.
CHECKSUM_KEY = "note_timeline_restrictions:body_checksum"

# Minutes after which an edit lock is considered stale and automatically released.
RESTRICTION_EXPIRY_MINUTES = 1


# ---------------------------------------------------------------------------
# Note-type access config — persisted via NoteTypeAccessConfig (CustomModel)
# ---------------------------------------------------------------------------


def get_access_config(note_type_id: str) -> list[str] | None:
    """Return the allowed staff IDs for a note type, or None if unrestricted."""
    return (
        NoteTypeAccessConfig.objects.filter(note_type_id=note_type_id)
        .values_list("allowed_staff_ids", flat=True)
        .first()
    )


def set_access_config(note_type_id: str, allowed_staff_ids: list[str] | None) -> None:
    """Set (or clear with None) the access restriction for a note type."""
    if allowed_staff_ids is None:
        NoteTypeAccessConfig.objects.filter(note_type_id=note_type_id).delete()
    else:
        NoteTypeAccessConfig.objects.update_or_create(
            note_type_id=note_type_id,
            defaults={"allowed_staff_ids": allowed_staff_ids},
        )


def all_access_configs() -> dict[str, list[str]]:
    """Return all configured note-type restrictions keyed by note type UUID."""
    return {
        row["note_type_id"]: row["allowed_staff_ids"]
        for row in NoteTypeAccessConfig.objects.values("note_type_id", "allowed_staff_ids")
    }


# ---------------------------------------------------------------------------
# Edit lock helpers
# ---------------------------------------------------------------------------


def _restriction_value(
    editor_staff_id: str | None,
    blur: bool = True,
    message: str = "This note is currently being edited by another user.",
) -> str:
    """Return a JSON string representing an active edit lock."""
    return json.dumps(
        {
            "active": True,
            "editor_staff_id": editor_staff_id,
            "blur": blur,
            "message": message,
            "last_edited_at": arrow.utcnow().isoformat(),
        }
    )


def _clear_restriction_value() -> str:
    """Return a JSON string that clears an edit lock."""
    return json.dumps({})


# ---------------------------------------------------------------------------
# Timeline configuration
# ---------------------------------------------------------------------------


class PatientTimelineHandler(BaseHandler):
    """Configures which note types are visible in the patient timeline."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_TIMELINE__GET_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """
        Evaluate note-type access rules and concurrent edit locks, returning a
        ``NoteRestrictionsEffect`` that controls the banner, blur, and edit-disabled
        state in the frontend.

        Policies are evaluated in order:

        1. **Note-type access** — if ``NoteTypeAccessConfig`` has a row for this note's
           type and the actor's staff ID is not in the allow-list, access is denied.
        2. **Concurrent edit lock** — if an active restriction exists in ``NoteMetadata``
           and the actor is not the lock holder, the restriction is surfaced with the
           stored blur and message values.

        Returns an empty list when the note is unrestricted.
        """
        """Write a restriction on the parent note and broadcast the change."""
        """
        Compare the current body checksum against the stored baseline.

        Returns a checksum upsert only when content is unchanged, or a checksum
        upsert + restriction write + ``NoteRestrictionsUpdatedEffect`` when it changed.
        """
        """Compute and store the initial body checksum for the newly created note."""
        """Exclude Message note types from the patient timeline for all actors."""
        message_note_types = NoteType.objects.filter(
            is_active=True, deprecated_at__isnull=True, name__in=["Message"]
        )
        note_type_ids = [str(nt.unique_identifier) for nt in message_note_types]
        return [PatientTimelineEffect(excluded_note_types=note_type_ids).apply()]


# ---------------------------------------------------------------------------
# Concurrent edit lock handlers
# ---------------------------------------------------------------------------


class TrackNoteBodyChecksum(BaseHandler):
    """
    Persists an initial body checksum when a note is created.

    This checksum is the baseline used by ``RestrictNoteOnConcurrentEdit`` to detect
    whether the note body has changed since the last save.
    """

    RESPONDS_TO = EventType.Name(EventType.NOTE_CREATED)

    def compute(self) -> list[Effect]:
        """Compute and store the initial body checksum for the newly created note."""
        note_id = UUID(self.event.target.id)
        try:
            note = Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return []
        return [
            NoteEffect(instance_id=note_id).upsert_metadata(
                key=CHECKSUM_KEY, value=note.body_checksum()
            )
        ]


class RestrictNoteOnConcurrentEdit(BaseHandler):
    """
    Applies an edit lock when a note's body is modified by a user.

    On every ``NOTE_UPDATED`` event the current body checksum is compared against the
    stored baseline.  If the content changed, an edit lock is written to NoteMetadata
    (key ``RESTRICTION_KEY``), attributing the lock to the staff member who made the edit.
    Other users who then open the note will see it restricted via ``NoteAccessPermissionsHandler``.

    The checksum baseline is always updated so subsequent saves from the same user do not
    re-trigger the lock.
    """

    RESPONDS_TO = EventType.Name(EventType.NOTE_UPDATED)

    def compute(self) -> list[Effect]:
        """
        Compare the current body checksum against the stored baseline.

        Returns a checksum upsert only when content is unchanged, or a checksum
        upsert + restriction write + ``NoteRestrictionsUpdatedEffect`` when it changed.
        """
        note_id = UUID(self.event.target.id)
        try:
            note = Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return []

        current_checksum = note.body_checksum()
        stored_checksum = (
            NoteMetadata.objects.filter(note__id=note_id, key=CHECKSUM_KEY)
            .values_list("value", flat=True)
            .first()
        )

        note_effect = NoteEffect(instance_id=note_id)
        upsert_checksum = note_effect.upsert_metadata(key=CHECKSUM_KEY, value=current_checksum)

        if stored_checksum is None or stored_checksum == current_checksum:
            return [upsert_checksum]

        editor_staff_id = self.event.context.get("user", {}).get("id")
        return [
            upsert_checksum,
            note_effect.upsert_metadata(
                key=RESTRICTION_KEY, value=_restriction_value(editor_staff_id)
            ),
            NoteRestrictionsUpdatedEffect(note_id=str(note_id)).apply(),
        ]


class RestrictNoteOnLetterEdit(BaseHandler):
    """
    Applies an edit lock to a note when its associated letter is updated.

    Because letter edits do not change the note body directly, the body checksum approach
    used by ``RestrictNoteOnConcurrentEdit`` would not detect them.  This handler fills that
    gap by writing an edit lock on the parent note whenever a ``LETTER_UPDATED`` event fires.
    """

    RESPONDS_TO = EventType.Name(EventType.LETTER_UPDATED)

    def compute(self) -> list[Effect]:
        """Write a restriction on the parent note and broadcast the change."""
        editor_staff_id = self.event.context.get("user", {}).get("id")
        note_id = (
            Letter.objects.filter(id=self.event.target.id)
            .values_list("note__id", flat=True)
            .first()
        )
        if not note_id:
            return []
        return [
            NoteEffect(instance_id=note_id).upsert_metadata(
                key=RESTRICTION_KEY, value=_restriction_value(editor_staff_id)
            ),
            NoteRestrictionsUpdatedEffect(note_id=str(note_id)).apply(),
        ]


class ExpireNoteRestrictionsCron(CronTask):
    """
    Automatically releases edit locks that have exceeded ``RESTRICTION_EXPIRY_MINUTES``.

    Runs every minute.  Any note whose edit lock was last refreshed more than
    ``RESTRICTION_EXPIRY_MINUTES`` ago has its lock cleared and a
    ``NoteRestrictionsUpdatedEffect`` emitted so connected clients immediately reflect the
    change.
    """

    SCHEDULE = "* * * * *"

    def execute(self) -> list[Effect]:
        """
        Scan all active restrictions and release any that have exceeded the expiry window.

        For each expired restriction: clears the ``NoteMetadata`` entry and emits a
        ``NoteRestrictionsUpdatedEffect`` so connected clients immediately reflect the change.
        """
        cutoff = arrow.utcnow().shift(minutes=-RESTRICTION_EXPIRY_MINUTES).isoformat()
        effects: list[Effect] = []

        for note_id, raw_value in NoteMetadata.objects.filter(key=RESTRICTION_KEY).values_list(
            "note__id", "value"
        ):
            try:
                data = json.loads(raw_value)
            except (json.JSONDecodeError, TypeError):
                continue

            last_edited_at = data.get("last_edited_at", "")
            if not last_edited_at or last_edited_at > cutoff:
                continue

            note_effect = NoteEffect(instance_id=note_id)
            effects.append(
                note_effect.upsert_metadata(key=RESTRICTION_KEY, value=_clear_restriction_value())
            )
            effects.append(NoteRestrictionsUpdatedEffect(note_id=str(note_id)).apply())

        return effects


# ---------------------------------------------------------------------------
# Permission resolution
# ---------------------------------------------------------------------------


class NoteAccessPermissionsHandler(BaseHandler):
    """
    Responds to ``GET_NOTE_RESTRICTIONS`` events with a ``NoteRestrictionsEffect``.

    Two restriction policies are evaluated in order:

    1. **Role-based restriction** — if the note type is ``RESTRICTED_NOTE_TYPE`` and the
       requesting user is not ``PRIVILEGED_ACTOR_ID``, access is denied and the note is
       blurred with an explanatory banner.

    2. **Concurrent edit lock** — if an active edit lock exists in NoteMetadata and the
       requesting user is not the staff member who holds the lock, the note is restricted
       according to the lock's ``blur`` and ``message`` settings.

    Returning no effects leaves the note unrestricted.
    """

    RESPONDS_TO = EventType.Name(EventType.GET_NOTE_RESTRICTIONS)

    def compute(self) -> list[Effect]:
        """
        Evaluate note-type access rules and concurrent edit locks, returning a
        ``NoteRestrictionsEffect`` that controls the banner, blur, and edit-disabled
        state in the frontend.

        Policies are evaluated in order:

        1. **Note-type access** — if ``NoteTypeAccessConfig`` has a row for this note's
           type and the actor's staff ID is not in the allow-list, access is denied.
        2. **Concurrent edit lock** — if an active restriction exists in ``NoteMetadata``
           and the actor is not the lock holder, the restriction is surfaced with the
           stored blur and message values.

        Returns an empty list when the note is unrestricted.
        """
        # --- Dynamic note-type access control (configured via the dashboard) ---
        note_type_id = (
            Note.objects.filter(id=self.event.target.id)
            .values_list("note_type_version__unique_identifier", flat=True)
            .first()
        )

        if note_type_id is not None:
            allowed = get_access_config(str(note_type_id))
            if allowed is not None:
                actor_staff_id = (
                    Staff.objects.filter(user__dbid=self.event.actor.id)
                    .values_list("id", flat=True)
                    .first()
                )
                if str(actor_staff_id) not in allowed:
                    return [
                        NoteRestrictionsEffect(
                            restrict_access=True,
                            blur_content=True,
                            banner_message="You don't have access to this note type.",
                        ).apply()
                    ]

        # --- Concurrent edit lock ---
        raw_lock = (
            NoteMetadata.objects.filter(note__id=self.event.target.id, key=RESTRICTION_KEY)
            .values_list("value", flat=True)
            .first()
        )
        if not raw_lock:
            return []

        data = json.loads(raw_lock)
        active = data.get("active", False)
        editor_staff_id = data.get("editor_staff_id")
        actor_staff_id = (
            Staff.objects.filter(user__dbid=self.event.actor.id)
            .values_list("id", flat=True)
            .first()
        )
        restrict_access = active and str(editor_staff_id) != str(actor_staff_id)

        return [
            NoteRestrictionsEffect(
                restrict_access=restrict_access,
                blur_content=restrict_access and data.get("blur", False),
                banner_message=data.get("message") if restrict_access else None,
            ).apply()
        ]

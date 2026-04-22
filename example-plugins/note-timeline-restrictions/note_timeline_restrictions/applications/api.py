import json
from http import HTTPStatus
from uuid import UUID

import arrow
from django.db.models import Q

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note as NoteEffect
from canvas_sdk.effects.note.restrictions_updated import NoteRestrictionsUpdatedEffect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api
from canvas_sdk.handlers.simple_api.security import StaffSessionAuthMixin
from canvas_sdk.v1.data import Note
from canvas_sdk.v1.data.note import NoteStates, NoteType
from canvas_sdk.v1.data.staff import Staff
from note_timeline_restrictions.handlers.event_handlers import (
    RESTRICTION_EXPIRY_MINUTES,
    RESTRICTION_KEY,
    _clear_restriction_value,
    _restriction_value,
    all_access_configs,
    set_access_config,
)


class NoteRestrictionApi(StaffSessionAuthMixin, SimpleAPI):
    """REST API backing the Note Access Restriction dashboard."""

    @api.get("/notes")
    def list_notes(self) -> list[Response | Effect]:
        """Return a paginated list of notes with their current edit lock status."""
        patient_search = self.request.query_params.get("patient_search", "").strip()
        state = self.request.query_params.get("state", "").strip()
        locked = self.request.query_params.get("locked", "").strip()
        page = int(self.request.query_params.get("page", 1))
        page_size = int(self.request.query_params.get("page_size", 25))

        queryset = (
            Note.objects.select_related("patient", "provider", "note_type_version", "current_state")
            .prefetch_related("metadata")
            .order_by("-datetime_of_service")
            .exclude(current_state__state__in=(NoteStates.DELETED, NoteStates.CANCELLED))
        )

        if patient_search:
            q = Q()
            for term in patient_search.split():
                q &= (
                    Q(patient__first_name__icontains=term)
                    | Q(patient__last_name__icontains=term)
                    | Q(patient__nickname__icontains=term)
                )
            queryset = queryset.filter(q)

        if state:
            queryset = queryset.filter(current_state__state=state)

        if locked == "true":
            queryset = queryset.filter(metadata__key=RESTRICTION_KEY)
        elif locked == "false":
            queryset = queryset.exclude(metadata__key=RESTRICTION_KEY)

        total_count = queryset.count()
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        notes_page = queryset[(page - 1) * page_size : page * page_size]

        notes = []
        for note in notes_page:
            lock_meta = next((m for m in note.metadata.all() if m.key == RESTRICTION_KEY), None)
            lock_data: dict = {}
            if lock_meta:
                try:  # noqa: SIM105
                    lock_data = json.loads(lock_meta.value)
                except (json.JSONDecodeError, TypeError):
                    pass

            active = lock_data.get("active", False)
            last_edited_at = lock_data.get("last_edited_at", "")
            expired = (
                bool(last_edited_at)
                and last_edited_at
                <= arrow.utcnow().shift(minutes=-RESTRICTION_EXPIRY_MINUTES).isoformat()
            )

            notes.append(
                {
                    "id": str(note.id),
                    "patient_name": (
                        f"{note.patient.first_name} {note.patient.last_name}"
                        if note.patient
                        else "Unknown"
                    ),
                    "patient_id": str(note.patient.id) if note.patient else None,
                    "provider": note.provider.credentialed_name if note.provider else "Unknown",
                    "note_title": note.note_type_version.name
                    if note.note_type_version
                    else "Untitled",
                    "dos": (
                        arrow.get(note.datetime_of_service).format("MMM DD, YYYY")
                        if note.datetime_of_service
                        else "N/A"
                    ),
                    "state": note.current_state.state if note.current_state else None,
                    "state_label": (
                        NoteStates(note.current_state.state).label
                        if note.current_state
                        else "Unknown"
                    ),
                    "locked": active and not expired,
                    "editor_staff_id": lock_data.get("editor_staff_id"),
                    "message": lock_data.get("message"),
                    "last_edited_at": last_edited_at,
                }
            )

        return [
            JSONResponse(
                {
                    "notes": notes,
                    "pagination": {
                        "current_page": page,
                        "total_pages": total_pages,
                        "total_count": total_count,
                        "page_size": page_size,
                        "has_previous": page > 1,
                        "has_next": page < total_pages,
                    },
                },
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/notes/<note_id>/unrestrict")
    def unnote_restrictions(self) -> list[Response | Effect]:
        """
        Remove the access restriction from a note.

        Clears the NoteMetadata restriction and broadcasts a NoteRestrictionsUpdatedEffect
        so all connected clients immediately update their view.
        """
        note_id = self.request.path_params["note_id"]

        if not Note.objects.filter(id=note_id).exists():
            return [JSONResponse({"error": "Note not found"}, status_code=HTTPStatus.NOT_FOUND)]

        note_effect = NoteEffect(instance_id=UUID(note_id))
        return [
            JSONResponse({"success": True}, status_code=HTTPStatus.OK),
            note_effect.upsert_metadata(key=RESTRICTION_KEY, value=_clear_restriction_value()),
            NoteRestrictionsUpdatedEffect(note_id=note_id).apply(),
        ]

    @api.post("/notes/<note_id>/restrict")
    def note_restrictions(self) -> list[Response | Effect]:
        """Manually apply an access restriction to a note."""
        note_id = self.request.path_params["note_id"]
        staff_id = self.request.headers.get("canvas-logged-in-user-id")

        if not Note.objects.filter(id=note_id).exists():
            return [JSONResponse({"error": "Note not found"}, status_code=HTTPStatus.NOT_FOUND)]

        try:
            body = self.request.json() or {}
        except Exception:
            body = {}
        note_effect = NoteEffect(instance_id=UUID(note_id))
        return [
            JSONResponse({"success": True}, status_code=HTTPStatus.OK),
            note_effect.upsert_metadata(
                key=RESTRICTION_KEY,
                value=_restriction_value(
                    editor_staff_id=staff_id,
                    blur=body.get("blur", True),
                    message=body.get(
                        "message", "This note is currently being edited by another user."
                    ),
                ),
            ),
            NoteRestrictionsUpdatedEffect(note_id=note_id).apply(),
        ]

    @api.get("/states")
    def list_states(self) -> list[Response | Effect]:
        """Return available note states for dashboard filtering."""
        states = [{"value": s[0], "label": s[1]} for s in NoteStates.choices]
        return [JSONResponse({"states": states}, status_code=HTTPStatus.OK)]

    # ------------------------------------------------------------------
    # Note-type access control
    # ------------------------------------------------------------------

    @api.get("/note-types")
    def list_note_types(self) -> list[Response | Effect]:
        """Return all active note types with their current access configuration."""
        configs = all_access_configs()
        note_types = []
        for nt in (
            NoteType.objects.filter(is_active=True, deprecated_at__isnull=True)
            .order_by("name")
            .values("unique_identifier", "name", "category")
        ):
            nt_id = str(nt["unique_identifier"])
            allowed = configs.get(nt_id)
            note_types.append(
                {
                    "id": nt_id,
                    "name": nt["name"],
                    "category": nt["category"],
                    "restricted": allowed is not None,
                    "allowed_staff_ids": allowed or [],
                }
            )
        return [JSONResponse({"note_types": note_types}, status_code=HTTPStatus.OK)]

    @api.put("/note-types/<note_type_id>/access")
    def set_note_type_access(self) -> list[Response | Effect]:
        """
        Configure which staff may access a note type.

        Body: ``{"allowed_staff_ids": ["<staff-uuid>", ...]}``
        Pass ``null`` for ``allowed_staff_ids`` (or omit the body) to remove the restriction.
        """
        note_type_id = self.request.path_params["note_type_id"]
        try:
            body = self.request.json() or {}
        except Exception:
            body = {}
        allowed = body.get("allowed_staff_ids")  # None = unrestricted

        set_access_config(note_type_id, allowed)
        return [
            JSONResponse(
                {"success": True, "note_type_id": note_type_id, "allowed_staff_ids": allowed},
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/staff")
    def list_staff(self) -> list[Response | Effect]:
        """Return active staff members for the access-control multi-select."""
        staff_list = [
            {
                "id": str(s.id),
                "name": s.credentialed_name,
            }
            for s in Staff.objects.filter(active=True).order_by("last_name", "first_name")
        ]
        return [JSONResponse({"staff": staff_list}, status_code=HTTPStatus.OK)]

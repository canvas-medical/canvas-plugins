import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class NoteTypeCategory(StrEnum):
    """api.NoteType.CATEGORY_CHOICES — only user-editable values can be set via SDK."""

    ENCOUNTER = "encounter"
    SCHEDULE_EVENT = "schedule_event"


class NoteType(TrackableFieldsModel):
    """
    Effect to create, update, or delete a NoteType.

    Only `encounter` and `schedule_event` categories are user-editable; other
    categories (appointment / letter / review / message / data / inpatient /
    ccda) are system-managed and will be rejected by the home-app interpreter.
    """

    class Meta:
        effect_type = "NOTE_TYPE"

    id: str | UUID | None = None
    name: str | None = None
    display: str | None = None
    code: str | None = None
    system: str | None = None
    category: NoteTypeCategory | None = Field(default=None, strict=False)
    rank: int | None = None
    icon: str | None = None
    is_scheduleable: bool | None = None
    is_default_appointment_type: bool | None = None
    is_scheduleable_via_patient_portal: bool | None = None
    online_duration: int | None = None
    is_telehealth: bool | None = None
    is_sig_required: bool | None = None
    is_patient_required: bool | None = None
    allow_custom_title: bool | None = None
    possible_durations: list[int] | None = None
    is_billable: bool | None = None
    defer_place_of_service_to_practice_location: bool | None = None
    default_place_of_service: str | None = None
    available_places_of_service: list[str] | None = None
    is_active: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "create":
            for required in ("name", "display", "category"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a note type.",
                            getattr(self, required),
                        )
                    )
        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a note type.",
                    self.id,
                )
            )
        return errors

    def create(self) -> Effect:
        """Build the CREATE effect."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Build the UPDATE effect."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Build the DELETE effect (carries only the id)."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("NoteType", "NoteTypeCategory")

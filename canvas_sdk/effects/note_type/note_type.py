from enum import StrEnum

from pydantic import Field

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class NoteTypeCategory(StrEnum):
    """Note type categories a plugin may create or edit."""

    ENCOUNTER = "encounter"
    SCHEDULE_EVENT = "schedule_event"


class NoteType(ConfigCrudEffect):
    """Create, update, or deactivate a note type.

    ``id`` is the note type's id (its ``unique_identifier``). Only ``encounter``
    and ``schedule_event`` note types can be written; other categories are
    system-managed. Delete deprecates the note type rather than removing it.
    """

    class Meta:
        effect_type = "NOTE_TYPE"

    _entity_label: str = "note type"
    _create_required: tuple[str, ...] = ("name", "display", "code", "system", "category", "icon")

    name: str | None = None
    display: str | None = None
    code: str | None = None
    system: str | None = None
    version: str | None = None
    category: NoteTypeCategory | None = Field(default=None, strict=False)
    icon: str | None = None
    rank: int | None = None
    is_active: bool | None = None
    is_visible: bool | None = None
    is_scheduleable: bool | None = None
    is_default_appointment_type: bool | None = None
    is_scheduleable_via_patient_portal: bool | None = None
    online_duration: int | None = None
    is_telehealth: bool | None = None
    is_billable: bool | None = None
    is_sig_required: bool | None = None
    is_patient_required: bool | None = None
    allow_custom_title: bool | None = None
    defer_place_of_service_to_practice_location: bool | None = None
    default_place_of_service: str | None = None
    available_places_of_service: list[str] | None = None


__exports__ = ("NoteType", "NoteTypeCategory")

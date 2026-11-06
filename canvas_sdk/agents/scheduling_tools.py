"""SDK-provided tools for scheduling, registered on :data:`standard_tools`.

``find_providers`` and ``find_appointment_slots`` read the practice's providers and the
open times the native booking screens offer. ``book_appointment``,
``reschedule_appointment``, and ``cancel_appointment`` change the run's patient's
appointments; unlike the chart drafts, each takes effect when applied, so an agent that
offers them to a person lists ``@scheduling_writes`` under ``tools.approve``.

``find_patient`` names the one patient a set of identifiers matches, for an agent that
books for whoever a person asks about. It needs the ``PATIENT_SEARCH`` capability, which
the platform grants only to a staff member who can see every patient. A tool still acts
on the run's patient: the patient a search names is for the agent to tell a person, or to
start a run about, not one the other tools act on.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from canvas_sdk.agents.capabilities import Capability
from canvas_sdk.agents.document_tools import _matching_patients
from canvas_sdk.agents.standard_tools import standard_tools
from canvas_sdk.agents.tool_registry import FilterSpec, require_patient_id
from canvas_sdk.effects.note.appointment import Appointment as AppointmentEffect
from canvas_sdk.utils.appointment_slots import AppointmentSlotsHttp, SlotSearchError
from canvas_sdk.v1.data import Appointment, Staff

# The chart's permissions: booking and rescheduling (which books the appointment again)
# check add_appointment; cancelling is a note state change, which checks both of the others.
ADD_APPOINTMENT = "api.add_appointment"
CANCEL_PERMISSIONS = ("api.change_appointment", "api.add_notestatechangeevent")
# The most open times one search returns; a person narrows the window for more.
MAX_SLOTS = 50
# The longest window one slot search covers, as the slot search allows.
MAX_SLOT_SEARCH_DAYS = 31


def _aware(value: str, name: str) -> datetime:
    """An ISO 8601 date-time with a time zone, as the slot search and bookings need."""
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} {value!r} is not an ISO 8601 date-time") from None
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must carry a time zone, such as 2026-11-12T09:00:00-05:00")
    return parsed


def _patients_appointment(appointment_id: str, patient_id: str) -> Appointment:
    """The run's patient's appointment ``appointment_id``, refusing anyone else's."""
    try:
        UUID(str(appointment_id))
    except ValueError:
        raise ValueError(f"{appointment_id!r} is not an appointment id") from None
    appointment = (
        Appointment.objects.filter(id=appointment_id, patient__id=patient_id)
        .only("id", "duration_minutes")
        .first()
    )
    if appointment is None:
        raise ValueError(
            f"No appointment {appointment_id!r} for this patient; use find_appointments."
        )
    return appointment


# Reads --------------------------------------------------------------------------------


@standard_tools.tool(
    name="find_patient",
    description=(
        "Find the one patient a person means, from the identifiers they give: the last "
        "name and birth date, plus the first name and MRN when known. Returns the "
        "patient's id only when exactly one patient matches; otherwise it says none or "
        "several did and names no one. Never loosen or guess identifiers to get a match: "
        "ask the person instead. The other tools still act on this run's patient, not the "
        "one found."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "first_name": {"type": "string", "description": "First name, or a nickname."},
            "last_name": {"type": "string", "description": "Last name."},
            "birth_date": {"type": "string", "format": "date", "description": "YYYY-MM-DD."},
            "mrn": {"type": "string", "description": "The patient's MRN, when known."},
        },
    },
    categories=("patient_search",),
    required_capabilities=(Capability.PATIENT_SEARCH,),
    returns_description=(
        "`{match: {patient_id}, matched_on}` when exactly one patient matches, else "
        "`{match: null, reason}`."
    ),
    progress_label="Finding the patient",
)
def _find_patient(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """The one patient the identifiers match, if exactly one does."""
    found, matched_on = _matching_patients(arguments)
    if len(found) != 1:
        reason = "No patient matches." if not found else "More than one patient matches; ask which."
        return {"match": None, "reason": reason}
    return {"match": {"patient_id": str(found[0].id)}, "matched_on": ", ".join(matched_on)}


@standard_tools.filter_search_tool(
    name="find_providers",
    description=(
        "List the practice's active staff a patient can be booked with, by name or "
        "primary location. Returns each with `id` (pass it as `provider_id` to the "
        "scheduling tools, or in `provider_ids` to `find_appointment_slots`), name, and "
        "primary location. Practice-level config, not patient-scoped."
    ),
    queryset_factory=lambda args, pid: Staff.objects.filter(active=True),
    filters={
        "name_contains": FilterSpec(
            type="string",
            description="Case-insensitive match on the first or last name.",
            apply=lambda qs, v: (
                qs.filter(first_name__icontains=v) | qs.filter(last_name__icontains=v)
            ),
        ),
        "practice_location_id": FilterSpec(
            type="string",
            description="Only staff whose primary location this is, from find_practice_locations.",
            apply=lambda qs, v: qs.filter(primary_practice_location__id=v),
        ),
    },
    ordering=("last_name", "first_name"),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results. Defaults to 25.",
    categories=("scheduling_reads",),
    model=Staff,
    citable=False,
    returns_description=("Array of objects with `id`, `name`, and `primary_practice_location_id`."),
    progress_label="Listing providers",
)
def _serialize_provider(staff: Any) -> dict[str, Any]:
    """Per-row serializer for find_providers."""
    location = staff.primary_practice_location
    return {
        "id": str(staff.id),
        "name": f"{staff.first_name} {staff.last_name}".strip(),
        "primary_practice_location_id": str(location.id) if location else None,
    }


@standard_tools.tool(
    name="find_appointment_slots",
    description=(
        "Search the open appointment times the native booking screens offer at one "
        "practice location, between two times (at most 31 days apart), for a visit of "
        "the given length. Narrow it to providers from find_providers and a visit type "
        "from find_note_types. A slot is not held: book soon after finding it, and search "
        "again if the booking is refused."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "practice_location_id": {
                "type": "string",
                "description": "The location, from find_practice_locations.",
            },
            "start": {
                "type": "string",
                "description": "Earliest start, ISO 8601 with a time zone.",
            },
            "end": {"type": "string", "description": "Latest start, ISO 8601 with a time zone."},
            "duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480},
            "provider_ids": {"type": "array", "items": {"type": "string"}},
            "visit_type_id": {
                "type": "string",
                "description": "The visit's note type, from find_note_types.",
            },
            "reschedule_appointment_id": {
                "type": "string",
                "description": "When rescheduling, the appointment, so its own time shows as open.",
            },
        },
        "required": ["practice_location_id", "start", "end", "duration_minutes"],
    },
    categories=("scheduling_reads",),
    returns_description=(
        f"Array of up to {MAX_SLOTS} `{{provider_id, start, end}}`, earliest first."
    ),
    progress_label="Searching open times",
)
def _find_appointment_slots(
    arguments: dict[str, Any], *, ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    """Open times as the native booking screens would offer them."""
    start = _aware(str(arguments["start"]), "start")
    end = _aware(str(arguments["end"]), "end")
    if end <= start or end - start > timedelta(days=MAX_SLOT_SEARCH_DAYS):
        raise ValueError(f"end must be after start and within {MAX_SLOT_SEARCH_DAYS} days of it")
    try:
        slots = AppointmentSlotsHttp().search_slots(
            location_id=str(arguments["practice_location_id"]),
            start=start,
            end=end,
            duration=int(arguments["duration_minutes"]),
            staff_ids=arguments.get("provider_ids") or None,
            visit_type_id=arguments.get("visit_type_id") or None,
            exclude_appointment_id=arguments.get("reschedule_appointment_id") or None,
        )
    except SlotSearchError as exc:
        raise ValueError(f"The slot search failed: {exc}") from exc
    return [
        {"provider_id": slot.staff_id, "start": slot.start.isoformat(), "end": slot.end.isoformat()}
        for slot in sorted(slots, key=lambda slot: slot.start)[:MAX_SLOTS]
    ]


# Writes -------------------------------------------------------------------------------


@standard_tools.tool(
    name="book_appointment",
    description=(
        "Book an appointment for this run's patient at a time find_appointment_slots "
        "offered. It takes effect when applied, not as a draft: confirm the time, "
        "provider, and visit type with the person first."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "provider_id": {"type": "string", "description": "From find_providers."},
            "practice_location_id": {
                "type": "string",
                "description": "From find_practice_locations.",
            },
            "visit_type_id": {
                "type": "string",
                "description": "A schedulable encounter note type, from find_note_types.",
            },
            "start_time": {"type": "string", "description": "ISO 8601 with a time zone."},
            "duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480},
        },
        "required": [
            "provider_id",
            "practice_location_id",
            "visit_type_id",
            "start_time",
            "duration_minutes",
        ],
    },
    categories=("scheduling_writes",),
    required_permissions=(ADD_APPOINTMENT,),
    effect_types=("CREATE_APPOINTMENT",),
    returns_description="`{ok: true, booked: false, requested: {...}}`: applied after the run.",
    progress_label="Booking the appointment",
)
def _book_appointment(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage the booking for the run's patient."""
    patient_id = require_patient_id(ctx)
    start_time = _aware(str(arguments["start_time"]), "start_time")
    effect = AppointmentEffect(
        patient_id=patient_id,
        provider_id=str(arguments["provider_id"]),
        practice_location_id=str(arguments["practice_location_id"]),
        appointment_note_type_id=str(arguments["visit_type_id"]),
        start_time=start_time,
        duration_minutes=int(arguments["duration_minutes"]),
    )
    ctx["effects"].append(effect.create())
    return {
        "ok": True,
        "booked": False,
        "requested": {
            "start_time": start_time.isoformat(),
            "provider_id": arguments["provider_id"],
        },
        "note": "The booking is applied after this run; check find_appointments to confirm it.",
    }


@standard_tools.tool(
    name="reschedule_appointment",
    description=(
        "Move one of this run's patient's appointments, from find_appointments, to a new "
        "time find_appointment_slots offered (pass reschedule_appointment_id there so the "
        "current time shows as open). Takes effect when applied: confirm with the person "
        "first. A patient already checked in cannot be rescheduled."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string", "description": "From find_appointments."},
            "start_time": {"type": "string", "description": "ISO 8601 with a time zone."},
            "provider_id": {"type": "string", "description": "A new provider, if changing."},
            "practice_location_id": {
                "type": "string",
                "description": "A new location, if changing.",
            },
            "duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480},
        },
        "required": ["appointment_id", "start_time"],
    },
    categories=("scheduling_writes",),
    required_permissions=(ADD_APPOINTMENT,),
    effect_types=("RESCHEDULE_APPOINTMENT",),
    returns_description="`{ok: true, appointment_id}`: applied after the run.",
    progress_label="Rescheduling the appointment",
)
def _reschedule_appointment(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage the move of the run's patient's appointment."""
    appointment = _patients_appointment(str(arguments["appointment_id"]), require_patient_id(ctx))
    changes: dict[str, Any] = {
        "start_time": _aware(str(arguments["start_time"]), "start_time"),
        "duration_minutes": int(arguments.get("duration_minutes") or appointment.duration_minutes),
    }
    for key in ("provider_id", "practice_location_id"):
        if arguments.get(key):
            changes[key] = str(arguments[key])
    effect = AppointmentEffect(instance_id=str(appointment.id), **changes)
    ctx["effects"].append(effect.reschedule())
    return {"ok": True, "appointment_id": str(appointment.id)}


@standard_tools.tool(
    name="cancel_appointment",
    description=(
        "Cancel one of this run's patient's appointments, from find_appointments. Takes "
        "effect when applied: confirm with the person first."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string", "description": "From find_appointments."},
        },
        "required": ["appointment_id"],
    },
    categories=("scheduling_writes",),
    required_permissions=CANCEL_PERMISSIONS,
    effect_types=("CANCEL_APPOINTMENT",),
    returns_description="`{ok: true, appointment_id}`: applied after the run.",
    progress_label="Cancelling the appointment",
)
def _cancel_appointment(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage the cancellation of the run's patient's appointment."""
    appointment = _patients_appointment(str(arguments["appointment_id"]), require_patient_id(ctx))
    ctx["effects"].append(AppointmentEffect(instance_id=str(appointment.id)).cancel())
    return {"ok": True, "appointment_id": str(appointment.id)}


__exports__ = ()

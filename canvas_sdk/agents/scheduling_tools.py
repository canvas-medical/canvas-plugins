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

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from canvas_sdk.agents.capabilities import Capability
from canvas_sdk.agents.document_tools import _matching_patients
from canvas_sdk.agents.standard_tools import standard_tools
from canvas_sdk.agents.tool_registry import FilterSpec, require_patient_id
from canvas_sdk.effects.note.appointment import Appointment as AppointmentEffect
from canvas_sdk.utils.appointment_slots import AppointmentSlotsHttp, SlotSearchError
from canvas_sdk.v1.data import Appointment, PracticeLocation, Staff

# The chart's permissions: booking and rescheduling (which books the appointment again)
# check add_appointment; cancelling is a note state change, which checks both of the others.
ADD_APPOINTMENT = "api.add_appointment"
CANCEL_PERMISSIONS = ("api.change_appointment", "api.add_notestatechangeevent")
# The most open times one search returns; a person narrows the window for more.
MAX_SLOTS = 50
# The longest window one slot search covers, as the slot search allows.
MAX_SLOT_SEARCH_DAYS = 31
# How far ahead an appointment may be booked or moved.
MAX_BOOKING_DAYS = 365
# The shortest and longest visit, in minutes.
MIN_DURATION_MINUTES = 5
MAX_DURATION_MINUTES = 480


def _aware(value: str, name: str) -> datetime:
    """An ISO 8601 date-time with a time zone, as the slot search and bookings need."""
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} {value!r} is not an ISO 8601 date-time") from None
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must carry a time zone, such as 2026-11-12T09:00:00-05:00")
    return parsed


def _start_time(value: str) -> datetime:
    """A booking's start: aware, not past, and within ``MAX_BOOKING_DAYS``."""
    start = _aware(value, "start_time")
    now = datetime.now(UTC)
    if start < now:
        raise ValueError("start_time is in the past; use a time find_appointment_slots offered")
    if start > now + timedelta(days=MAX_BOOKING_DAYS):
        raise ValueError(f"start_time is more than {MAX_BOOKING_DAYS} days ahead")
    return start


def _duration(value: Any) -> int:
    """A visit length in minutes, within the bounds a booking allows."""
    minutes = int(value)
    if not MIN_DURATION_MINUTES <= minutes <= MAX_DURATION_MINUTES:
        raise ValueError(
            f"duration_minutes must be {MIN_DURATION_MINUTES} to {MAX_DURATION_MINUTES}"
        )
    return minutes


def _active_provider(provider_id: str) -> str:
    """``provider_id``, which must name active staff."""
    if not _is_uuid(provider_id) or not Staff.objects.filter(id=provider_id, active=True).exists():
        raise ValueError(f"No active provider {provider_id!r}; use find_providers.")
    return provider_id


def _active_location(location_id: str) -> str:
    """``location_id``, which must name an active practice location."""
    if (
        not _is_uuid(location_id)
        or not PracticeLocation.objects.filter(id=location_id, active=True).exists()
    ):
        raise ValueError(f"No active location {location_id!r}; use find_practice_locations.")
    return location_id


def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def _patients_appointment(appointment_id: str, patient_id: str) -> Appointment:
    """The run's patient's appointment ``appointment_id``, refusing anyone else's."""
    if not _is_uuid(appointment_id):
        raise ValueError(f"{appointment_id!r} is not an appointment id")
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
        "Find the one patient a person means, from the identifiers they give: the first "
        "name, last name, and birth date, plus the MRN when known. Returns the "
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
        "required": ["first_name", "last_name", "birth_date"],
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
    """The one patient the identifiers match, if exactly one does.

    The first name is required: a last name and birth date alone can name another person
    in the same family.
    """
    if not str(arguments.get("first_name") or "").strip():
        raise ValueError("Pass the patient's first name too; ask the person for it.")
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
    patient_scoped=False,
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
            "duration_minutes": {
                "type": "integer",
                "minimum": MIN_DURATION_MINUTES,
                "maximum": MAX_DURATION_MINUTES,
            },
            "provider_ids": {"type": "array", "items": {"type": "string"}},
            "visit_type_id": {
                "type": "string",
                "description": "The visit's note type, from find_note_types.",
            },
            "reschedule_appointment_id": {
                "type": "string",
                "description": (
                    "When rescheduling, the patient's appointment, from find_appointments, "
                    "so its own time shows as open."
                ),
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
    # Only the run's patient's own appointment opens up its time.
    rescheduling = None
    if reschedule_appointment_id := arguments.get("reschedule_appointment_id"):
        rescheduling = str(
            _patients_appointment(str(reschedule_appointment_id), require_patient_id(ctx)).id
        )
    try:
        slots = AppointmentSlotsHttp().search_slots(
            location_id=str(arguments["practice_location_id"]),
            start=start,
            end=end,
            duration=_duration(arguments["duration_minutes"]),
            staff_ids=arguments.get("provider_ids") or None,
            visit_type_id=arguments.get("visit_type_id") or None,
            exclude_appointment_id=rescheduling,
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
            "start_time": {
                "type": "string",
                "description": "ISO 8601 with a time zone, at most a year ahead.",
            },
            "duration_minutes": {
                "type": "integer",
                "minimum": MIN_DURATION_MINUTES,
                "maximum": MAX_DURATION_MINUTES,
            },
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
    start_time = _start_time(str(arguments["start_time"]))
    effect = AppointmentEffect(
        patient_id=patient_id,
        provider_id=_active_provider(str(arguments["provider_id"])),
        practice_location_id=_active_location(str(arguments["practice_location_id"])),
        appointment_note_type_id=str(arguments["visit_type_id"]),
        start_time=start_time,
        duration_minutes=_duration(arguments["duration_minutes"]),
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
        "current time shows as open). Canvas cancels the appointment and books a new one "
        "with a new id, which find_appointments returns once applied. Takes effect when "
        "applied: confirm with the person first. A patient already checked in cannot be "
        "rescheduled."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "appointment_id": {"type": "string", "description": "From find_appointments."},
            "start_time": {
                "type": "string",
                "description": "ISO 8601 with a time zone, at most a year ahead.",
            },
            "provider_id": {"type": "string", "description": "A new provider, if changing."},
            "practice_location_id": {
                "type": "string",
                "description": "A new location, if changing.",
            },
            "duration_minutes": {
                "type": "integer",
                "minimum": MIN_DURATION_MINUTES,
                "maximum": MAX_DURATION_MINUTES,
            },
        },
        "required": ["appointment_id", "start_time"],
    },
    categories=("scheduling_writes",),
    required_permissions=(ADD_APPOINTMENT,),
    effect_types=("RESCHEDULE_APPOINTMENT",),
    returns_description=(
        "`{ok: true, replaces_appointment_id, requested: {start_time}, note}`: applied after "
        "the run, as a new appointment."
    ),
    progress_label="Rescheduling the appointment",
)
def _reschedule_appointment(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage the move of the run's patient's appointment."""
    appointment = _patients_appointment(str(arguments["appointment_id"]), require_patient_id(ctx))
    changes: dict[str, Any] = {
        "start_time": _start_time(str(arguments["start_time"])),
        "duration_minutes": _duration(
            arguments.get("duration_minutes") or appointment.duration_minutes
        ),
    }
    if arguments.get("provider_id"):
        changes["provider_id"] = _active_provider(str(arguments["provider_id"]))
    if arguments.get("practice_location_id"):
        changes["practice_location_id"] = _active_location(str(arguments["practice_location_id"]))
    effect = AppointmentEffect(instance_id=str(appointment.id), **changes)
    ctx["effects"].append(effect.reschedule())
    return {
        "ok": True,
        "replaces_appointment_id": str(appointment.id),
        "requested": {"start_time": changes["start_time"].isoformat()},
        "note": (
            "Applied after this run: Canvas cancels this appointment and books a new one "
            "with a new id. Use find_appointments for the new appointment's id."
        ),
    }


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

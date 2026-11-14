"""The scheduling tools: providers, open times, and the run's patient's appointments."""

import json
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest

from canvas_sdk.agents import Capability, ToolNotAllowed, scheduling_tools, standard_tools
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    NoteFactory,
    NoteTypeFactory,
    PatientFactory,
    PracticeLocationFactory,
    StaffFactory,
)
from canvas_sdk.utils.appointment_slots import Slot, SlotSearchError
from canvas_sdk.v1.data import Appointment
from canvas_sdk.v1.data.note import NoteTypeCategories

# Bookings must be ahead of now, so the times are relative to it.
START = (datetime.now(UTC) + timedelta(days=3)).replace(hour=9, minute=0, second=0, microsecond=0)
LATER = (START + timedelta(days=1, hours=1)).isoformat()


def _ctx(patient: Any = None, **extra: Any) -> dict[str, Any]:
    return {"patient_id": patient.id if patient else None, "effects": [], **extra}


def _data(effect: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(effect.payload)["data"]
    return data


def _appointment(patient: Any) -> Appointment:
    note = NoteFactory.create(patient=patient)
    return Appointment.objects.create(
        patient=patient,
        note=note,
        note_type=note.note_type_version,
        provider=note.provider,
        location=note.location,
        start_time=START,
        duration_minutes=30,
        status="confirmed",
        telehealth_instructions_sent=False,
    )


# Patient search ---------------------------------------------------------------------


@pytest.mark.django_db
def test_find_patient_names_only_the_one_patient_the_identifiers_match() -> None:
    """One match names the patient; several name no one."""
    birth = date(1980, 4, 2)
    patient = PatientFactory.create(first_name="Ada", last_name="Lovelace", birth_date=birth)
    PatientFactory.create(first_name="Ann", last_name="Byron", birth_date=birth)
    PatientFactory.create(first_name="Ann", last_name="Byron", birth_date=birth)
    run = _ctx(capabilities=frozenset({Capability.PATIENT_SEARCH}))

    one = standard_tools.execute(
        "find_patient",
        {"first_name": "Ada", "last_name": "Lovelace", "birth_date": "1980-04-02"},
        ctx=run,
    )
    several = standard_tools.execute(
        "find_patient",
        {"first_name": "Ann", "last_name": "Byron", "birth_date": "1980-04-02"},
        ctx=run,
    )

    assert one["match"] == {"patient_id": patient.id}
    assert several["match"] is None and "More than one" in several["reason"]


@pytest.mark.django_db
def test_find_patient_needs_the_first_name() -> None:
    """A last name and birth date alone can name another person in the family."""
    PatientFactory.create(first_name="John", last_name="Doe", birth_date=date(1980, 4, 2))

    with pytest.raises(ValueError, match="first_name"):
        standard_tools.execute(
            "find_patient",
            {"last_name": "Doe", "birth_date": "1980-04-02"},
            ctx=_ctx(capabilities=frozenset({Capability.PATIENT_SEARCH})),
        )


@pytest.mark.django_db
def test_find_patient_needs_the_patient_search_capability() -> None:
    """Without it, the run cannot search among every patient."""
    with pytest.raises(ToolNotAllowed):
        standard_tools.execute(
            "find_patient", {"last_name": "Lovelace", "birth_date": "1980-04-02"}, ctx=_ctx()
        )


# Providers and open times -----------------------------------------------------------


@pytest.mark.django_db
def test_find_providers_lists_active_staff_by_location() -> None:
    """Inactive staff and other locations are left out."""
    location = PracticeLocationFactory.create()
    here = StaffFactory.create(
        first_name="Grace", last_name="Hopper", primary_practice_location=location
    )
    StaffFactory.create(last_name="Gone", active=False, primary_practice_location=location)
    StaffFactory.create(last_name="Elsewhere")

    rows = standard_tools.execute(
        "find_providers",
        {"practice_location_id": str(location.id)},
        ctx=_ctx(PatientFactory.create()),
    )

    assert [(r["id"], r["name"]) for r in rows] == [(str(here.id), "Grace Hopper")]


def test_find_appointment_slots_searches_as_the_booking_screens_do(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The window, length, providers, and visit type pass through; times come back sorted."""
    asked: dict[str, Any] = {}

    def search(self: Any, **kwargs: Any) -> list[Slot]:
        asked.update(kwargs)
        later = Slot("s2", START + timedelta(hours=2), START + timedelta(hours=2, minutes=30))
        return [later, Slot("s1", START, START + timedelta(minutes=30))]

    monkeypatch.setattr(scheduling_tools.AppointmentSlotsHttp, "search_slots", search)

    slots = standard_tools.execute(
        "find_appointment_slots",
        {
            "practice_location_id": "loc-1",
            "start": "2026-11-12T08:00:00+00:00",
            "end": "2026-11-13T08:00:00+00:00",
            "duration_minutes": 30,
            "provider_ids": ["s1", "s2"],
            "visit_type_id": "vt-1",
        },
        ctx=_ctx(),
    )

    assert [s["provider_id"] for s in slots] == ["s1", "s2"]
    assert (
        asked["location_id"],
        asked["duration"],
        asked["staff_ids"],
        asked["visit_type_id"],
    ) == (
        "loc-1",
        30,
        ["s1", "s2"],
        "vt-1",
    )


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        ("2026-11-12T08:00:00", "2026-11-13T08:00:00+00:00", "time zone"),
        ("2026-11-12T08:00:00+00:00", "2026-12-20T08:00:00+00:00", "within 31 days"),
    ],
)
def test_a_slot_search_without_a_time_zone_or_past_31_days_is_refused(
    start: str, end: str, message: str
) -> None:
    """The slot search needs aware times and a window it allows."""
    with pytest.raises(ValueError, match=message):
        standard_tools.execute(
            "find_appointment_slots",
            {"practice_location_id": "l", "start": start, "end": end, "duration_minutes": 30},
            ctx=_ctx(),
        )


def test_a_failed_slot_search_goes_back_to_the_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canvas refusing the search is a tool error the model can act on."""

    def search(self: Any, **kwargs: Any) -> list[Slot]:
        raise SlotSearchError(400, "location_id names no location")

    monkeypatch.setattr(scheduling_tools.AppointmentSlotsHttp, "search_slots", search)

    with pytest.raises(ValueError, match="names no location"):
        standard_tools.execute(
            "find_appointment_slots",
            {
                "practice_location_id": "nope",
                "start": "2026-11-12T08:00:00+00:00",
                "end": "2026-11-13T08:00:00+00:00",
                "duration_minutes": 30,
            },
            ctx=_ctx(),
        )


# Booking, rescheduling, cancelling --------------------------------------------------


@pytest.mark.django_db
def test_a_booking_is_for_the_runs_patient() -> None:
    """The patient comes from the run, never from the model."""
    patient = PatientFactory.create()
    provider = StaffFactory.create()
    location = PracticeLocationFactory.create()
    visit = NoteTypeFactory.create(
        category=NoteTypeCategories.ENCOUNTER, is_scheduleable=True, is_active=True
    )
    ctx = _ctx(patient)

    result = standard_tools.execute(
        "book_appointment",
        {
            "provider_id": str(provider.id),
            "practice_location_id": str(location.id),
            "visit_type_id": str(visit.id),
            "start_time": START.isoformat(),
            "duration_minutes": 30,
        },
        ctx=ctx,
    )

    (effect,) = ctx["effects"]
    data = _data(effect)
    assert (result["ok"], result["booked"]) == (True, False)
    assert (data["patient_id"], data["provider_id"], data["duration_minutes"]) == (
        patient.id,
        str(provider.id),
        30,
    )


@pytest.mark.django_db
def test_booking_needs_a_patient_run() -> None:
    """A run about no patient has no one to book."""
    with pytest.raises(ValueError, match="not about a patient"):
        standard_tools.execute(
            "book_appointment",
            {
                "provider_id": "p",
                "practice_location_id": "l",
                "visit_type_id": "v",
                "start_time": START.isoformat(),
                "duration_minutes": 30,
            },
            ctx=_ctx(),
        )


@pytest.mark.django_db
def test_a_reschedule_says_it_books_a_new_appointment() -> None:
    """Canvas cancels the original and books a new one, so the old id is not the live one."""
    patient = PatientFactory.create()
    original = _appointment(patient)

    result = standard_tools.execute(
        "reschedule_appointment",
        {"appointment_id": str(original.id), "start_time": LATER},
        ctx=_ctx(patient),
    )

    assert result["replaces_appointment_id"] == str(original.id)
    assert "appointment_id" not in result
    assert result["requested"] == {"start_time": LATER}
    assert "find_appointments" in result["note"]


@pytest.mark.django_db
def test_an_appointment_is_rescheduled_and_cancelled_only_for_the_runs_patient() -> None:
    """Another patient's appointment id is refused, as if it did not exist."""
    patient, other = PatientFactory.create(), PatientFactory.create()
    mine, theirs = _appointment(patient), _appointment(other)
    ctx = _ctx(patient)

    standard_tools.execute(
        "reschedule_appointment",
        {"appointment_id": str(mine.id), "start_time": LATER},
        ctx=ctx,
    )
    standard_tools.execute("cancel_appointment", {"appointment_id": str(mine.id)}, ctx=ctx)

    rescheduled, cancelled = (_data(effect) for effect in ctx["effects"])
    assert (rescheduled["instance_id"], rescheduled["duration_minutes"]) == (str(mine.id), 30)
    assert cancelled["instance_id"] == str(mine.id)
    for tool in ("reschedule_appointment", "cancel_appointment"):
        with pytest.raises(ValueError, match="No appointment"):
            standard_tools.execute(
                tool,
                {"appointment_id": str(theirs.id), "start_time": LATER},
                ctx=_ctx(patient),
            )


def _booking(provider: Any, location: Any, **changes: Any) -> dict[str, Any]:
    visit = NoteTypeFactory.create(
        category=NoteTypeCategories.ENCOUNTER, is_scheduleable=True, is_active=True
    )
    return {
        "provider_id": str(provider.id),
        "practice_location_id": str(location.id),
        "visit_type_id": str(visit.id),
        "start_time": START.isoformat(),
        "duration_minutes": 30,
    } | changes


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"start_time": "1900-01-01T09:00:00+00:00"}, "in the past"),
        ({"start_time": "2199-01-01T09:00:00+00:00"}, "365 days ahead"),
        ({"start_time": "2030-01-01T09:00:00"}, "time zone"),
    ],
)
def test_a_booking_outside_now_to_a_year_ahead_is_refused(
    changes: dict[str, Any], message: str
) -> None:
    """A start in the past, past the horizon, or without a time zone stages nothing."""
    ctx = _ctx(PatientFactory.create())
    booking = _booking(StaffFactory.create(), PracticeLocationFactory.create(), **changes)

    with pytest.raises(ValueError, match=message):
        standard_tools.execute("book_appointment", booking, ctx=ctx)
    assert ctx["effects"] == []


@pytest.mark.parametrize("minutes", [-30, 0, 4, 481, 100_000])
def test_a_duration_outside_5_to_480_minutes_is_refused_in_code(minutes: int) -> None:
    """The tool refuses the length itself, past the schema."""
    with pytest.raises(ValueError, match="duration_minutes must be 5 to 480"):
        scheduling_tools._duration(minutes)


@pytest.mark.django_db
def test_a_booking_with_an_inactive_provider_or_location_is_refused() -> None:
    """Only active staff and practice locations take bookings."""
    ctx = _ctx(PatientFactory.create())
    active_location = PracticeLocationFactory.create()

    with pytest.raises(ValueError, match="No active provider"):
        standard_tools.execute(
            "book_appointment",
            _booking(StaffFactory.create(active=False), active_location),
            ctx=ctx,
        )
    with pytest.raises(ValueError, match="No active location"):
        standard_tools.execute(
            "book_appointment",
            _booking(StaffFactory.create(), PracticeLocationFactory.create(active=False)),
            ctx=ctx,
        )
    assert ctx["effects"] == []


@pytest.mark.django_db
def test_a_reschedule_checks_the_new_time_and_any_new_provider() -> None:
    """Moving an appointment meets the same bounds as booking one."""
    patient = PatientFactory.create()
    appointment = _appointment(patient)
    ctx = _ctx(patient)

    with pytest.raises(ValueError, match="in the past"):
        standard_tools.execute(
            "reschedule_appointment",
            {"appointment_id": str(appointment.id), "start_time": "1900-01-01T09:00:00+00:00"},
            ctx=ctx,
        )
    with pytest.raises(ValueError, match="No active provider"):
        standard_tools.execute(
            "reschedule_appointment",
            {
                "appointment_id": str(appointment.id),
                "start_time": LATER,
                "provider_id": str(StaffFactory.create(active=False).id),
            },
            ctx=ctx,
        )
    assert ctx["effects"] == []


@pytest.mark.django_db
def test_only_the_runs_patients_appointment_opens_its_time_in_a_slot_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Another patient's appointment, or none at all without a patient, is refused."""
    asked: dict[str, Any] = {}

    def search(self: Any, **kwargs: Any) -> list[Slot]:
        asked.update(kwargs)
        return []

    monkeypatch.setattr(scheduling_tools.AppointmentSlotsHttp, "search_slots", search)
    patient, other = PatientFactory.create(), PatientFactory.create()
    mine, theirs = _appointment(patient), _appointment(other)
    window = {
        "practice_location_id": "loc-1",
        "start": START.isoformat(),
        "end": LATER,
        "duration_minutes": 30,
    }

    standard_tools.execute(
        "find_appointment_slots",
        window | {"reschedule_appointment_id": str(mine.id)},
        ctx=_ctx(patient),
    )

    assert asked["exclude_appointment_id"] == str(mine.id)
    with pytest.raises(ValueError, match="No appointment"):
        standard_tools.execute(
            "find_appointment_slots",
            window | {"reschedule_appointment_id": str(theirs.id)},
            ctx=_ctx(patient),
        )
    with pytest.raises(ValueError, match="not about a patient"):
        standard_tools.execute(
            "find_appointment_slots",
            window | {"reschedule_appointment_id": str(mine.id)},
            ctx=_ctx(),
        )


@pytest.mark.django_db
def test_find_appointments_leaves_out_an_appointment_entered_in_error() -> None:
    """One entered in error never happened, so it is not a visit the model can cite."""
    patient = PatientFactory.create()
    kept = _appointment(patient)
    gone = _appointment(patient)
    gone.entered_in_error = CanvasUserFactory.create()
    gone.save()

    rows = standard_tools.execute("find_appointments", {}, ctx={"patient_id": patient.id})

    assert [row["id"] for row in rows] == [str(kept.id)]


@pytest.mark.django_db
@pytest.mark.parametrize("first_name", ["", "   "], ids=["empty", "blank"])
def test_find_patient_needs_a_first_name(first_name: str) -> None:
    """A last name and birth date alone can name another person in the same family."""
    patient = PatientFactory.create()

    with pytest.raises(ValueError, match="first name"):
        standard_tools.execute(
            "find_patient",
            {
                "first_name": first_name,
                "last_name": patient.last_name,
                "birth_date": patient.birth_date.isoformat(),
            },
            ctx={"capabilities": frozenset({Capability.PATIENT_SEARCH})},
        )

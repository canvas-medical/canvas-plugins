"""Tests for room booking models, relationships, and constraints.

Exercises:
- Factories for SDK models (Patient, Staff) and their proxies
- Factories for CustomModels (Room, RoomBooking, StaffBookable)
- CRUD operations on CustomModels
- ForeignKey and ManyToMany traversal
- CASCADE deletion behavior
- UniqueConstraint violation
- proxy_field descriptor (NoteProxy)
- Reverse relation lookups
"""

from datetime import UTC, datetime

import factory
import pytest
from custom_data_room_booking.models.proxy import NoteProxy, PatientProxy, StaffProxy
from custom_data_room_booking.models.room import Room, RoomBooking
from custom_data_room_booking.models.staff_bookable import StaffBookable
from django.db import IntegrityError

from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory, StaffFactory

# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


class StaffProxyFactory(StaffFactory, factory.django.DjangoModelFactory[StaffProxy]):
    """Factory for StaffProxy, inheriting default field values from StaffFactory."""

    class Meta:
        model = StaffProxy


class PatientProxyFactory(PatientFactory, factory.django.DjangoModelFactory[PatientProxy]):
    """Factory for PatientProxy, inheriting default field values from PatientFactory."""

    class Meta:
        model = PatientProxy


class RoomFactory(factory.django.DjangoModelFactory[Room]):
    """Factory for Room with auto-incrementing names ('Room 1', 'Room 2', ...)."""

    class Meta:
        model = Room

    name = factory.Sequence(lambda n: f"Room {n + 1}")


class StaffBookableFactory(factory.django.DjangoModelFactory[StaffBookable]):
    """Factory for StaffBookable, auto-creating a StaffProxy via SubFactory."""

    class Meta:
        model = StaffBookable

    staff = factory.SubFactory(StaffProxyFactory)


class RoomBookingFactory(factory.django.DjangoModelFactory[RoomBooking]):
    """Factory for RoomBooking, auto-creating Room, Staff, and Patient via SubFactories."""

    class Meta:
        model = RoomBooking

    room = factory.SubFactory(RoomFactory)
    staff = factory.SubFactory(StaffProxyFactory)
    patient = factory.SubFactory(PatientProxyFactory)
    scheduled_at = factory.Sequence(lambda n: datetime(2026, 3, 15, 9 + n, 0, 0, tzinfo=UTC))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def staff() -> StaffProxy:
    """A factory for StaffProxy, inheriting default field values from StaffFactory."""
    return StaffProxyFactory.create()


@pytest.fixture
def patient() -> PatientProxy:
    """A factory for PatientProxy, inheriting default field values from PatientFactory."""
    return PatientProxyFactory.create()


@pytest.fixture
def room() -> Room:
    """A factory for Rooms."""
    return RoomFactory.create()


# ---------------------------------------------------------------------------
# Room CRUD
# ---------------------------------------------------------------------------


def test_create_room() -> None:
    """Create a Room and verify dbid is assigned and name is persisted."""
    room = RoomFactory.create(name="Exam Room A")
    assert room.dbid is not None
    assert room.name == "Exam Room A"


def test_read_room() -> None:
    """Fetch a Room by dbid and verify its name."""
    room = RoomFactory.create(name="Exam Room B")
    fetched = Room.objects.get(dbid=room.dbid)
    assert fetched.name == "Exam Room B"


def test_update_room() -> None:
    """Update a Room's name and verify the change is persisted."""
    room = RoomFactory.create(name="Old Name")
    room.name = "New Name"
    room.save()
    assert Room.objects.get(dbid=room.dbid).name == "New Name"


def test_delete_room() -> None:
    """Delete a Room and verify it no longer exists."""
    room = RoomFactory.create()
    dbid = room.dbid
    room.delete()
    assert not Room.objects.filter(dbid=dbid).exists()


# ---------------------------------------------------------------------------
# RoomBooking CRUD
# ---------------------------------------------------------------------------


def test_create_booking(room: Room, staff: StaffProxy, patient: PatientProxy) -> None:
    """Create a RoomBooking and verify its FK relations are set correctly."""
    booking = RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    assert booking.dbid is not None
    assert booking.room == room
    assert booking.staff.dbid == staff.dbid
    assert booking.patient.dbid == patient.dbid


def test_booking_factory_creates_related_objects() -> None:
    """RoomBookingFactory auto-creates related Room, Staff, and Patient."""
    booking = RoomBookingFactory.create()
    assert booking.room.dbid is not None
    assert booking.staff.dbid is not None
    assert booking.patient.dbid is not None
    assert booking.scheduled_at is not None


# ---------------------------------------------------------------------------
# StaffBookable
# ---------------------------------------------------------------------------


def test_create_staff_bookable(staff: StaffProxy) -> None:
    """Create a StaffBookable and verify it links to the correct staff."""
    bookable = StaffBookable.objects.create(staff=staff)
    assert bookable.dbid is not None
    assert bookable.staff.dbid == staff.dbid


def test_staff_bookable_reverse_relation(staff: StaffProxy) -> None:
    """staff.bookable reverse OneToOne relation resolves correctly."""
    StaffBookable.objects.create(staff=staff)
    assert staff.bookable.dbid is not None


def test_staff_bookable_unique_per_staff(staff: StaffProxy) -> None:
    """OneToOneField prevents duplicate StaffBookable for the same staff."""
    StaffBookable.objects.create(staff=staff)
    with pytest.raises(IntegrityError):
        StaffBookable.objects.create(staff=staff)


# ---------------------------------------------------------------------------
# ForeignKey traversal
# ---------------------------------------------------------------------------


def test_booking_staff_is_staff_proxy(room: Room, staff: StaffProxy, patient: PatientProxy) -> None:
    """ForeignKey to StaffProxy returns a Staff instance (base class)."""
    booking = RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    fetched = RoomBooking.objects.select_related("staff").get(dbid=booking.dbid)
    assert fetched.staff.first_name == staff.first_name


def test_booking_patient_is_patient_proxy(
    room: Room, staff: StaffProxy, patient: PatientProxy
) -> None:
    """ForeignKey to PatientProxy returns a Patient instance (base class)."""
    booking = RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    fetched = RoomBooking.objects.select_related("patient").get(dbid=booking.dbid)
    assert fetched.patient.first_name == patient.first_name


# ---------------------------------------------------------------------------
# Reverse relations
# ---------------------------------------------------------------------------


def test_room_bookings_reverse_relation(
    room: Room, staff: StaffProxy, patient: PatientProxy
) -> None:
    """room.bookings reverse manager returns the room's bookings."""
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 9, 0, 0, tzinfo=UTC),
    )
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    assert room.bookings.count() == 2


def test_staff_room_bookings_reverse(staff: StaffProxy) -> None:
    """staff.room_bookings reverse FK manager returns bookings for that staff."""
    RoomBookingFactory.create(staff=staff)
    RoomBookingFactory.create(staff=staff)
    assert staff.room_bookings.count() == 2


def test_patient_bookings_reverse(patient: PatientProxy) -> None:
    """patient.patient_bookings reverse FK manager returns bookings for that patient."""
    RoomBookingFactory.create(patient=patient)
    assert patient.patient_bookings.count() == 1


# ---------------------------------------------------------------------------
# ManyToMany traversal
# ---------------------------------------------------------------------------


def test_room_staff_m2m(room: Room, staff: StaffProxy, patient: PatientProxy) -> None:
    """room.staff M2M through RoomBooking includes booked staff."""
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    assert staff in room.staff.all()


def test_room_patients_m2m(room: Room, staff: StaffProxy, patient: PatientProxy) -> None:
    """room.patients M2M through RoomBooking includes booked patients."""
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    assert patient in room.patients.all()


# ---------------------------------------------------------------------------
# CASCADE deletion
# ---------------------------------------------------------------------------


def test_delete_room_cascades_to_bookings(
    room: Room, staff: StaffProxy, patient: PatientProxy
) -> None:
    """Deleting a Room should CASCADE-delete its RoomBooking records."""
    b1 = RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 9, 0, 0, tzinfo=UTC),
    )
    b2 = RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    assert room.bookings.count() == 2
    room.delete()
    assert not RoomBooking.objects.filter(dbid__in=[b1.dbid, b2.dbid]).exists()
    assert not Room.objects.filter(dbid=room.dbid).exists()


def test_delete_room_does_not_delete_staff(
    room: Room, staff: StaffProxy, patient: PatientProxy
) -> None:
    """Deleting a Room leaves referenced Staff intact (DO_NOTHING)."""
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    room.delete()
    assert StaffProxy.objects.filter(dbid=staff.dbid).exists()


def test_delete_room_does_not_delete_patient(
    room: Room, staff: StaffProxy, patient: PatientProxy
) -> None:
    """Deleting a Room leaves referenced Patient intact (DO_NOTHING)."""
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    room.delete()
    assert PatientProxy.objects.filter(dbid=patient.dbid).exists()


# ---------------------------------------------------------------------------
# UniqueConstraint on RoomBooking (room + scheduled_at)
# ---------------------------------------------------------------------------


def test_unique_room_scheduled_at(room: Room, staff: StaffProxy, patient: PatientProxy) -> None:
    """Two bookings for the same room and time should violate the constraint."""
    other_staff = StaffProxyFactory.create()
    other_patient = PatientProxyFactory.create()
    ts = datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC)

    RoomBooking.objects.create(room=room, staff=staff, patient=patient, scheduled_at=ts)
    with pytest.raises(IntegrityError):
        RoomBooking.objects.create(
            room=room, staff=other_staff, patient=other_patient, scheduled_at=ts
        )


def test_same_time_different_rooms(staff: StaffProxy, patient: PatientProxy) -> None:
    """Bookings in different rooms at the same time should be allowed."""
    room_a = RoomFactory.create(name="Room A")
    room_b = RoomFactory.create(name="Room B")
    ts = datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC)

    RoomBooking.objects.create(room=room_a, staff=staff, patient=patient, scheduled_at=ts)
    RoomBooking.objects.create(room=room_b, staff=staff, patient=patient, scheduled_at=ts)

    assert RoomBooking.objects.count() == 2


def test_same_room_different_times(room: Room, staff: StaffProxy, patient: PatientProxy) -> None:
    """Bookings in the same room at different times should be allowed."""
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 9, 0, 0, tzinfo=UTC),
    )
    RoomBooking.objects.create(
        room=room,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    assert RoomBooking.objects.count() == 2


# ---------------------------------------------------------------------------
# proxy_field (NoteProxy)
# ---------------------------------------------------------------------------


def test_note_proxy_patient_returns_patient_proxy() -> None:
    """NoteProxy.patient should return a PatientProxy with display_name."""
    note = NoteFactory.create()
    proxy_note = NoteProxy.objects.select_related("patient").get(dbid=note.dbid)
    assert proxy_note.patient is not None
    assert hasattr(proxy_note.patient, "display_name")
    assert proxy_note.patient.display_name == f"{note.patient.first_name} {note.patient.last_name}"


def test_note_proxy_provider_returns_staff_proxy() -> None:
    """NoteProxy.provider should return a StaffProxy with display_name."""
    note = NoteFactory.create()
    proxy_note = NoteProxy.objects.select_related("provider").get(dbid=note.dbid)
    assert proxy_note.provider is not None
    assert hasattr(proxy_note.provider, "display_name")
    assert (
        proxy_note.provider.display_name == f"{note.provider.first_name} {note.provider.last_name}"
    )


def test_note_proxy_null_patient() -> None:
    """NoteProxy.patient should return None when the FK is null."""
    note = NoteFactory.create(patient=None)
    proxy_note = NoteProxy.objects.get(dbid=note.dbid)
    assert proxy_note.patient is None


def test_note_proxy_null_provider() -> None:
    """NoteProxy.provider should return None when the FK is null."""
    note = NoteFactory.create()
    # Clear the provider after creation to avoid NoteFactory's post-generation hooks.
    from canvas_sdk.v1.data import Note

    Note.objects.filter(dbid=note.dbid).update(provider=None)
    proxy_note = NoteProxy.objects.get(dbid=note.dbid)
    assert proxy_note.provider is None


def test_note_proxy_patient_class_is_patient_proxy() -> None:
    """proxy_field should swap __class__ to PatientProxy, not just return Patient."""
    note = NoteFactory.create()
    proxy_note = NoteProxy.objects.select_related("patient").get(dbid=note.dbid)
    assert type(proxy_note.patient) is PatientProxy


def test_note_proxy_provider_class_is_staff_proxy() -> None:
    """proxy_field should swap __class__ to StaffProxy, not just return Staff."""
    note = NoteFactory.create()
    proxy_note = NoteProxy.objects.select_related("provider").get(dbid=note.dbid)
    assert type(proxy_note.provider) is StaffProxy


# ---------------------------------------------------------------------------
# Proxy model display_name property
# ---------------------------------------------------------------------------


def test_staff_proxy_display_name(staff: StaffProxy) -> None:
    """StaffProxy.display_name returns 'first last'."""
    assert staff.display_name == f"{staff.first_name} {staff.last_name}"


def test_patient_proxy_display_name(patient: PatientProxy) -> None:
    """PatientProxy.display_name returns 'first last'."""
    assert patient.display_name == f"{patient.first_name} {patient.last_name}"


# ---------------------------------------------------------------------------
# Querying and filtering
# ---------------------------------------------------------------------------


def test_filter_bookings_by_room(staff: StaffProxy, patient: PatientProxy) -> None:
    """Filter RoomBooking queryset by room FK."""
    room_a = RoomFactory.create(name="Room A")
    room_b = RoomFactory.create(name="Room B")

    RoomBooking.objects.create(
        room=room_a,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    )
    RoomBooking.objects.create(
        room=room_b,
        staff=staff,
        patient=patient,
        scheduled_at=datetime(2026, 3, 15, 11, 0, 0, tzinfo=UTC),
    )

    assert RoomBooking.objects.filter(room=room_a).count() == 1
    assert RoomBooking.objects.filter(room=room_b).count() == 1


def test_filter_bookings_by_staff() -> None:
    """Filter RoomBooking queryset by staff FK."""
    staff_a = StaffProxyFactory.create()
    staff_b = StaffProxyFactory.create()

    RoomBookingFactory.create(staff=staff_a)
    RoomBookingFactory.create(staff=staff_a)
    RoomBookingFactory.create(staff=staff_b)

    assert RoomBooking.objects.filter(staff=staff_a).count() == 2
    assert RoomBooking.objects.filter(staff=staff_b).count() == 1


def test_filter_bookings_by_patient() -> None:
    """Filter RoomBooking queryset by patient FK."""
    patient_a = PatientProxyFactory.create()
    patient_b = PatientProxyFactory.create()

    RoomBookingFactory.create(patient=patient_a)
    RoomBookingFactory.create(patient=patient_b)
    RoomBookingFactory.create(patient=patient_b)

    assert RoomBooking.objects.filter(patient=patient_a).count() == 1
    assert RoomBooking.objects.filter(patient=patient_b).count() == 2


def test_select_related_on_bookings() -> None:
    """select_related should avoid N+1 queries on staff and patient."""
    RoomBookingFactory.create_batch(3)
    bookings = list(RoomBooking.objects.select_related("room", "staff", "patient").all())
    assert len(bookings) == 3
    for b in bookings:
        assert b.room.name is not None
        assert b.staff.first_name is not None
        assert b.patient.first_name is not None

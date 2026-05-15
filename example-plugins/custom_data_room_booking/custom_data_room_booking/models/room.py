from __future__ import annotations

from datetime import datetime

from django.db.models import (
    CASCADE,
    DO_NOTHING,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    TextField,
    UniqueConstraint,
)

from canvas_sdk.v1.data.base import CustomModel
from custom_data_room_booking.models.proxy import PatientProxy, StaffProxy


class Room(CustomModel):
    """A bookable room with M2M links to staff and patients via RoomBooking."""

    name: TextField[str, str] = TextField()
    staff: ManyToManyField[StaffProxy, RoomBooking] = ManyToManyField(
        StaffProxy, through="RoomBooking", related_name="booked_rooms"
    )
    patients: ManyToManyField[PatientProxy, RoomBooking] = ManyToManyField(
        PatientProxy, through="RoomBooking", related_name="booked_rooms"
    )


class RoomBooking(CustomModel):
    """A scheduled booking linking a Room, Staff member, and Patient."""

    room: ForeignKey[Room, Room] = ForeignKey(
        Room, to_field="dbid", on_delete=CASCADE, related_name="bookings"
    )
    staff: ForeignKey[StaffProxy, StaffProxy] = ForeignKey(
        StaffProxy, to_field="dbid", on_delete=DO_NOTHING, related_name="room_bookings"
    )
    patient: ForeignKey[PatientProxy, PatientProxy] = ForeignKey(
        PatientProxy, to_field="dbid", on_delete=DO_NOTHING, related_name="patient_bookings"
    )
    scheduled_at: DateTimeField[str | datetime, datetime] = DateTimeField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["room", "scheduled_at"],
                name="unique_room_scheduled_at",
            ),
        ]

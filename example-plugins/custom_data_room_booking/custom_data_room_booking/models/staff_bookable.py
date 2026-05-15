from __future__ import annotations

from django.db.models import DO_NOTHING, OneToOneField

from canvas_sdk.v1.data.base import CustomModel
from custom_data_room_booking.models.proxy import StaffProxy


class StaffBookable(CustomModel):
    """Marks a staff member as eligible for room bookings."""

    staff: OneToOneField[StaffProxy, StaffProxy] = OneToOneField(
        StaffProxy, to_field="dbid", on_delete=DO_NOTHING, related_name="bookable"
    )

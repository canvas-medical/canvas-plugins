import dataclasses
import functools
import os
from collections.abc import Sequence
from datetime import datetime
from typing import Any

import requests

from canvas_sdk.utils.http import JsonOnlyResponse, ServiceClient


class SlotSearchError(RuntimeError):
    """Raised when Canvas could not search appointment slots.

    Attributes:
        status_code: The HTTP status code Canvas returned, or 0 if Canvas was never reached.
            400 means the search named something Canvas does not have, and the message names
            the field. 503 means Canvas could not read the provider calendars.
        message: The error message describing the failure.
    """

    def __init__(self, status_code: int, message: str):
        """Initialize a SlotSearchError.

        Args:
            status_code: The HTTP status code Canvas returned, or 0 if never reached.
            message: The error message describing the failure.
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@dataclasses.dataclass(frozen=True)
class Slot:
    """An open appointment time with one provider.

    Attributes:
        staff_id: The provider's id, as exposed on `Staff.id`.
        start: When the appointment would start, in the installation's time zone.
        end: When the appointment would end, in the installation's time zone.
    """

    staff_id: str
    start: datetime
    end: datetime


def _parse_slots(payload: Any) -> list[Slot] | None:
    """Read the slots out of a response body, or return None if it is not one."""
    if not isinstance(payload, dict) or not isinstance(payload.get("slots"), list):
        return None

    try:
        return [
            Slot(
                staff_id=slot["staff_id"],
                start=datetime.fromisoformat(slot["start"]),
                end=datetime.fromisoformat(slot["end"]),
            )
            for slot in payload["slots"]
        ]
    except (KeyError, TypeError, ValueError):
        return None


class AppointmentSlotsHttp(ServiceClient):
    """
    A client for Canvas's native appointment slot search.

    The search is the one the native booking screens use: it expands recurring availability
    and its exceptions, subtracts booked appointments and holds, and applies the visit type.
    Its base URL is Canvas itself, so only `search_slots` is exported.
    """

    __exports__ = ("search_slots",)

    def __init__(self) -> None:
        # CANVAS_PUBLIC_HOST is the instance's own URL and is required by its settings. The
        # runner does not share a listening port with the web process, so an address that
        # resolves only inside the web container reaches nothing.
        super().__init__(base_url=os.getenv("CANVAS_PUBLIC_HOST", ""))

    def search_slots(
        self,
        location_id: str,
        start: datetime,
        end: datetime,
        duration: int,
        staff_ids: Sequence[str] | None = None,
        visit_type_id: str | None = None,
        exclude_appointment_id: str | None = None,
        grid_minutes: int = 15,
        respect_holds: bool = True,
    ) -> list[Slot]:
        """Return the open appointment times the native booking screens would offer.

        Each call runs a new search. A slot is a snapshot, not a hold, so search again just
        before a booking.

        Args:
            location_id: The practice location, as exposed on `PracticeLocation.id`.
            start: The start of the search. It must carry a time zone. Add the practice's
                minimum notice here, for example `now + timedelta(hours=24)`. Canvas rounds
                it up to the next grid stop.
            end: The end of the search. It must carry a time zone, and it must be at most
                31 days after start.
            duration: The visit length in minutes.
            staff_ids: The providers to search, as exposed on `Staff.id`. Leave it out to
                search every schedulable provider.
            visit_type_id: The visit type, as exposed on `NoteType.id`. Availability limited
                to other visit types is left out.
            exclude_appointment_id: An appointment being rescheduled, as exposed on
                `Appointment.id`. Its own time is offered as open.
            grid_minutes: The spacing of slot start times, from 1 to 60.
            respect_holds: Apply the same-day and next-day holds on the calendars.

        Raises:
            ValueError: If start or end has no time zone.
            SlotSearchError: If Canvas refused the search, could not read the provider
                calendars, or could not be reached.
        """
        for name, value in (("start", start), ("end", end)):
            if value.tzinfo is None:
                raise ValueError(f"{name} must carry a time zone.")

        payload: dict[str, Any] = {
            "location_id": location_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "duration": duration,
            "grid_minutes": grid_minutes,
            "respect_holds": respect_holds,
        }

        if staff_ids is not None:
            payload["staff_ids"] = list(staff_ids)

        if visit_type_id is not None:
            payload["visit_type_id"] = visit_type_id

        if exclude_appointment_id is not None:
            payload["exclude_appointment_id"] = exclude_appointment_id

        try:
            response = JsonOnlyResponse(
                self._send(
                    "/appointment-slots/search/",
                    functools.partial(self._http_client.post, json=payload),
                )
            )
        except requests.RequestException:
            response = None

        if response is None:
            # Re-raise as the one type this module documents, outside the except block so
            # no error holding the request is chained to it.
            raise SlotSearchError(0, "Could not reach Canvas to search appointment slots.")

        if response.status_code != 200:
            raise SlotSearchError(
                response.status_code,
                f"Canvas could not search appointment slots: {response.json()}",
            )

        slots = _parse_slots(response.json())

        if slots is None:
            raise SlotSearchError(
                response.status_code,
                "The appointment slot search returned an unexpected response.",
            )

        return slots


appointment_slots_http = AppointmentSlotsHttp()

__all__ = __exports__ = (
    "Slot",
    "SlotSearchError",
    "appointment_slots_http",
)

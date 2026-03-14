from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPI, api
from custom_data_room_booking.models.proxy import NoteProxy, PatientProxy, StaffProxy
from custom_data_room_booking.models.room import Room, RoomBooking
from custom_data_room_booking.models.staff_bookable import StaffBookable


class RoomBookingAPI(SimpleAPI):
    """API for managing rooms, bookings, staff availability, and notes."""

    PREFIX = ""

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Validate the request's API key against the stored secret."""
        return credentials.key == self.secrets["my-api-key"]

    @api.get("/staff")
    def list_staff(self) -> list[Response | Effect]:
        """Return up to 50 staff members with id and display name."""
        staff = StaffProxy.objects.all()[:50]
        return [
            JSONResponse(
                {
                    "staff": [
                        {
                            "id": str(s.id),
                            "name": s.display_name,
                        }
                        for s in staff
                    ]
                }
            )
        ]

    @api.post("/rooms")
    def create_room(self) -> list[Response | Effect]:
        """Create a new room. Requires a JSON body with a 'name' field."""
        body = self.request.json()
        name = body.get("name")
        if not name:
            return [JSONResponse({"error": "name is required"}, status_code=HTTPStatus.BAD_REQUEST)]
        room = Room.objects.create(name=name)
        return [
            JSONResponse({"dbid": room.dbid, "name": room.name}, status_code=HTTPStatus.CREATED)
        ]

    @api.delete("/rooms/<id>")
    def delete_room(self) -> list[Response | Effect]:
        """Delete a room by dbid. Cascades to its bookings."""
        room_id = self.request.path_params["id"]
        try:
            room = Room.objects.get(dbid=room_id)
        except Room.DoesNotExist:
            return [JSONResponse({"error": "Room not found"}, status_code=HTTPStatus.NOT_FOUND)]
        room_name = room.name
        room.delete()
        return [JSONResponse({"deleted": room_name})]

    @api.get("/rooms/<id>/schedule")
    def get_room_schedule(self) -> list[Response | Effect]:
        """Return all bookings for a room with staff and patient details."""
        room_id = self.request.path_params["id"]
        try:
            room = Room.objects.get(dbid=room_id)
        except Room.DoesNotExist:
            return [JSONResponse({"error": "Room not found"}, status_code=HTTPStatus.NOT_FOUND)]

        bookings = RoomBooking.objects.filter(room=room).select_related("staff", "patient")
        schedule = []
        for b in bookings:
            schedule.append(
                {
                    "dbid": b.dbid,
                    "staff": {
                        "id": str(b.staff.id),
                        "name": b.staff.display_name,
                    },
                    "patient": {
                        "id": str(b.patient.id),
                        "name": b.patient.display_name,
                    },
                    "scheduled_at": str(b.scheduled_at),
                }
            )
        return [
            JSONResponse({"room": {"dbid": room.dbid, "name": room.name}, "schedule": schedule})
        ]

    @api.post("/staff/<id>/bookable")
    def make_bookable(self) -> list[Response | Effect]:
        """Mark a staff member as bookable. Idempotent."""
        staff_id = self.request.path_params["id"]
        try:
            staff = StaffProxy.objects.get(id=staff_id)
        except StaffProxy.DoesNotExist:
            return [JSONResponse({"error": "Staff not found"}, status_code=HTTPStatus.NOT_FOUND)]

        bookable, created = StaffBookable.objects.get_or_create(staff=staff)
        if not created:
            return [JSONResponse({"message": f"Staff {staff.display_name} is already bookable"})]
        return [
            JSONResponse(
                {"message": f"Staff {staff.display_name} is now bookable"},
                status_code=HTTPStatus.CREATED,
            )
        ]

    @api.get("/notes")
    def list_notes(self) -> list[Response | Effect]:
        """List recent notes with patient info."""
        notes = (
            NoteProxy.objects.select_related("patient", "provider")
            .filter(patient__isnull=False)
            .order_by("-dbid")[:20]
        )
        return [
            JSONResponse(
                {
                    "notes": [
                        {
                            "dbid": n.dbid,
                            "patient": n.patient.display_name if n.patient else None,
                            "provider": n.provider.display_name if n.provider else None,
                        }
                        for n in notes
                    ]
                }
            )
        ]

    @api.get("/notes/<id>")
    def get_note(self) -> list[Response | Effect]:
        """Fetch a note using NoteProxy so related patient/provider are proxy instances."""
        note_id = self.request.path_params["id"]
        try:
            note = NoteProxy.objects.select_related("patient", "provider").get(dbid=note_id)
        except NoteProxy.DoesNotExist:
            return [JSONResponse({"error": "Note not found"}, status_code=HTTPStatus.NOT_FOUND)]

        # note.patient and note.provider are PatientProxy/StaffProxy thanks to proxy_field,
        # so .display_name is available without extra queries.
        return [
            JSONResponse(
                {
                    "dbid": note.dbid,
                    "patient": note.patient.display_name if note.patient else None,
                    "provider": note.provider.display_name if note.provider else None,
                }
            )
        ]

    @api.post("/bookings")
    def create_booking(self) -> list[Response | Effect]:
        """Create a booking for a room, staff member, and patient at a given time."""
        body = self.request.json()
        room_id = body.get("room_id")
        staff_id = body.get("staff_id")
        patient_id = body.get("patient_id")
        scheduled_at = body.get("scheduled_at")

        if not all([room_id, staff_id, patient_id, scheduled_at]):
            return [
                JSONResponse(
                    {"error": "room_id, staff_id, patient_id, and scheduled_at are required"},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

        try:
            room = Room.objects.get(dbid=room_id)
        except Room.DoesNotExist:
            return [JSONResponse({"error": "Room not found"}, status_code=HTTPStatus.NOT_FOUND)]

        try:
            staff = StaffProxy.objects.get(id=staff_id)
        except StaffProxy.DoesNotExist:
            return [JSONResponse({"error": "Staff not found"}, status_code=HTTPStatus.NOT_FOUND)]

        if not StaffBookable.objects.filter(staff=staff).exists():
            return [
                JSONResponse(
                    {"error": f"Staff {staff.display_name} is not bookable"},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

        try:
            patient = PatientProxy.objects.get(id=patient_id)
        except PatientProxy.DoesNotExist:
            return [JSONResponse({"error": "Patient not found"}, status_code=HTTPStatus.NOT_FOUND)]

        booking = RoomBooking.objects.create(
            room=room,
            staff=staff,
            patient=patient,
            scheduled_at=scheduled_at,
        )
        return [
            JSONResponse(
                {
                    "dbid": booking.dbid,
                    "room": room.name,
                    "staff": staff.display_name,
                    "patient": patient.display_name,
                    "scheduled_at": str(booking.scheduled_at),
                },
                status_code=HTTPStatus.CREATED,
            )
        ]

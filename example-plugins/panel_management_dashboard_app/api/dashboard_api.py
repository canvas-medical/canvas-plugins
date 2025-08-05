import json
from http import HTTPStatus

import arrow

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api
from canvas_sdk.handlers.simple_api.security import StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus
from canvas_sdk.v1.data.note import NoteTypeCategories
from canvas_sdk.v1.data.practicelocation import PracticeLocation
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.task import Task, TaskStatus
from logger import log


class DashboardAPI(StaffSessionAuthMixin, SimpleAPI):
    """API for the panel management dashboard application."""

    PREFIX = "/app"

    # Serve templated HTML
    @api.get("/")
    def index(self) -> list[Response | Effect]:
        """Serve the main dashboard page."""
        log.info("DashboardAPI GET request for dashboard page.")
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])
        locations = PracticeLocation.objects.all()

        context = {
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
            "locations": [
                {
                    "id": location.id,
                    "short_name": location.short_name,
                    "full_name": location.full_name,
                }
                for location in locations
            ],
        }

        return [
            HTMLResponse(
                render_to_string("static/index.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/dashboard")
    def get_dashboard(self) -> list[Response | Effect]:
        """Serve the dashboard page with patient data."""
        log.info("DashboardAPI GET request for dashboard data.")
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])
        locations = PracticeLocation.objects.all()
        current_location_id = self.request.query_params.get("location_id")
        current_location = (
            PracticeLocation.objects.get(id=current_location_id) if current_location_id else None
        )

        context = {
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
            "locations": [
                {
                    "id": location.id,
                    "short_name": location.short_name,
                    "full_name": location.full_name,
                    "is_active": "active" if current_location_id == str(location.id) else "",
                }
                for location in locations
            ],
            "current_location": current_location,
            "active": "active" if not current_location else "",
            "page": int(self.request.query_params.get("page", 1)),
            "limit": int(self.request.query_params.get("limit", 10)),
        }

        return [
            HTMLResponse(
                render_to_string("static/dashboard.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/table")
    def get_table(self) -> list[Response | Effect]:
        """Serve the contents of a table with pagination."""
        log.info("DashboardAPI GET request for table data.")

        # Get pagination parameters from query string
        page = int(self.request.query_params.get("page", 1))
        limit = min(int(self.request.query_params.get("limit", 10)), 10)
        log.info(f"Pagination parameters: page={page}, limit={limit}")
        location_id = self.request.query_params.get("location_id")
        log.info(f"Location ID from query params: {location_id}")
        location = PracticeLocation.objects.get(id=location_id) if location_id else None
        staff = self._get_staff()

        # Calculate offset
        offset = (page - 1) * limit

        # Get patients with prefetched relationships
        patients_query = (
            Patient.objects.prefetch_related(
                "telecom",
                "notes",
                "notes__provider",
                "notes__note_type_version",
            )
            .filter(
                notes__note_type_version__category=NoteTypeCategories.ENCOUNTER,
            )
            .distinct()
        )

        if location:
            log.info(f"Filtering patients by location: {location.short_name}")
            patients_query = patients_query.filter(notes__location=location)

        # Get total count for pagination info
        total_count = patients_query.count()

        # Apply pagination
        patients_page = patients_query[offset : offset + limit]

        processed_patients = []
        for patient in patients_page:
            log.info(f"Processing patient: {patient.id}")

            # Create patient data object
            patient_data = {
                "id": patient.id,
                "photo_url": "https://d3hn0m4rbsz438.cloudfront.net/avatar1.png",
                "name": patient.preferred_full_name,
                "age": int(patient.age_at(arrow.now())),
                "gender": patient.sex_at_birth,
                "telecom": patient.telecom.first().value if patient.telecom.exists() else "N/A",
                "provider": patient.notes.filter(location=location).first().provider
                if patient.notes.filter(location=location).exists()
                else "N/A",
                "last_visit": patient.notes.filter(location=location).first().datetime_of_service
                if patient.notes.filter(location=location).exists()
                else "N/A",
                "location": location.short_name if location else "N/A",
                "tasks": self._get_patients_tasks(patient),
            }
            processed_patients.append(patient_data)

        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_previous = page > 1

        context = {
            "patients": processed_patients,
            "location": location,
            "staff": [
                {
                    "id": member.get("staff__id"),
                    "first_name": member.get("staff__first_name"),
                    "last_name": member.get("staff__last_name"),
                }
                for member in staff
            ],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "limit": limit,
                "has_next": has_next,
                "has_previous": has_previous,
                "next_page": page + 1 if has_next else None,
                "previous_page": page - 1 if has_previous else None,
            },
        }

        return [
            Response(
                render_to_string("static/table.html", context).encode(),
                status_code=HTTPStatus.OK,
            )
        ]

    # Serve the contents of a css file
    @api.get("/styles.css")
    def get_css(self) -> list[Response | Effect]:
        """Serve the contents of a CSS file."""
        return [
            Response(
                render_to_string("static/styles.css").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/css",
            )
        ]

    def _get_staff(self):
        return (
            CareTeamMembership.objects.filter(
                status=CareTeamMembershipStatus.ACTIVE,
            )
            .values(
                "staff__id",
                "staff__first_name",
                "staff__last_name",
                "role__display",
            )
            .distinct()
        )

    def _get_patients_tasks(self, patient) -> dict[str, int]:
        return {
            "all": Task.objects.filter(patient=patient).count(),
            "open": Task.objects.filter(
                patient=patient,
                status=TaskStatus.OPEN,
            ).count(),
        }

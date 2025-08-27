from http import HTTPStatus
from urllib.parse import urlencode

import arrow
from django.db.models import Count, Q

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api
from canvas_sdk.handlers.simple_api.security import StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus
from canvas_sdk.v1.data.coverage import CoverageStack
from canvas_sdk.v1.data.facility import Facility
from canvas_sdk.v1.data.note import NoteStates, NoteTypeCategories
from canvas_sdk.v1.data.protocol_current import ProtocolCurrent
from canvas_sdk.v1.data.protocol_result import ProtocolResultStatus
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.task import Task, TaskStatus
from logger import log


class DashboardAPI(StaffSessionAuthMixin, SimpleAPI):
    """API for the panel management dashboard application."""

    PREFIX = "/app"

    DEFAULT_PAGE_SIZE = 10

    DEFAULT_VISIT_THRESHOLD = "1 day"

    DEFAULT_AVATAR = "https://d3hn0m4rbsz438.cloudfront.net/avatar1.png"

    # Serve templated HTML
    @api.get("/")
    def index(self) -> list[Response | Effect]:
        """Serve the main dashboard page."""
        return [
            HTMLResponse(
                render_to_string("static/index.html", self._current_logged_staff),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/dashboard")
    def get_dashboard(self) -> list[Response | Effect]:
        """Serve the dashboard page with patient data."""
        facility_search = self.request.query_params.get("facility_search", "").strip()
        if facility_search:
            facilities = Facility.objects.filter(name__icontains=facility_search)
        else:
            facilities = Facility.objects.all()

        selected_facility_id = self.request.query_params.get("facility_id")
        selected_facility = (
            Facility.objects.get(id=selected_facility_id) if selected_facility_id else None
        )

        context = {
            "facilities": facilities,
            "selected_facility": selected_facility,
            "facility_search": facility_search,
            "page": int(self.request.query_params.get("page", 1)),
            "table_url": self._create_paginated_table_url(
                1, selected_facility_id, None, facility_search, None
            ),
        }

        return [
            HTMLResponse(
                render_to_string("static/dashboard.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/facilities")
    def get_facilities(self) -> list[Response | Effect]:
        """Serve the facilities list."""
        facility_search = self.request.query_params.get("facility_search", "").strip()
        if facility_search:
            facilities = Facility.objects.filter(name__icontains=facility_search)
        else:
            facilities = Facility.objects.all()

        selected_facility_id = self.request.query_params.get("facility_id")
        selected_facility = (
            Facility.objects.get(id=selected_facility_id) if selected_facility_id else None
        )

        context = {
            "facilities": facilities,
            "selected_facility": selected_facility,
            "facility_search": facility_search,
        }

        return [
            HTMLResponse(
                render_to_string("static/facilities.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/table")
    def get_table(self) -> list[Response | Effect]:
        """Serve the contents of a table with pagination."""
        # Get pagination parameters from query string
        page = int(self.request.query_params.get("page", 1))
        page_size = self._page_size

        # Search query
        patient_search = self.request.query_params.get("patient_search", "").strip()
        log.info(f"Patient search query: {patient_search}")

        # Facilities
        facility_id = self.request.query_params.get("facility_id")
        facility = Facility.objects.get(id=facility_id) if facility_id else None

        # Staff
        staff = self._get_staff()
        current_staff_id = self.request.query_params.get("staff_id")
        current_staff = (
            [member for member in staff if member["id"] == current_staff_id]
            if current_staff_id
            else None
        )
        current_staff = current_staff[0] if current_staff else None

        # Secrets
        secrets = self._get_secrets()

        # Calculate offset
        offset = (page - 1) * page_size

        # Get patients with prefetched relationships
        patients_query = Patient.objects.prefetch_related(
            "telecom",
            "addresses",
            "notes",
            "notes__provider",
            "notes__note_type_version",
            "notes__current_state",
        )

        if facility_id:
            patients_query = patients_query.filter(
                addresses__patientfacilityaddress__facility__id=facility_id
            )

        if current_staff_id:
            patients_query = patients_query.filter(notes__provider__id=current_staff_id)

        if patient_search:
            patients_query = patients_query.filter(
                Q(*[
                    Q(first_name__icontains=search_chunk) | Q(last_name__icontains=search_chunk)
                    for search_chunk in patient_search.split()
                ])
            )

        patients_query = patients_query.distinct()

        # Get total count for pagination info
        total_count = patients_query.count()
        # Apply pagination
        patients_page = patients_query[offset : offset + page_size]

        processed_patients = []
        for patient in patients_page:
            last_visit = self._get_last_visit(patient)
            gaps, total_gaps = self._get_gaps(patient)

            # Create patient data object
            patient_data = {
                "id": patient.id,
                # TODO investigate if patient avatars can be used in this context
                "photo_url": self.DEFAULT_AVATAR,
                "url": f"/patients/{patient.id}",
                "name": patient.preferred_full_name,
                "age": int(patient.age_at(arrow.now())),
                "gender": patient.sex_at_birth,
                "telecom": patient.telecom.first().value if patient.telecom.exists() else None,
                "last_visit": arrow.get(last_visit.datetime_of_service).format("MM.DD.YYYY")
                if last_visit
                else None,
                "provider": last_visit.provider if last_visit else None,
                "provider_role": self._get_staff_role_for_last_visit(patient, last_visit.provider)
                if last_visit and last_visit.provider
                else None,
                "tasks": self._get_patients_tasks(patient),
                "gaps": {
                    "due": gaps,
                    "total": total_gaps,
                },
                "insurance": self._get_coverage(patient=patient),
                "insurances": secrets.get("insurances_logos"),
                "sticky_note": "",
            }
            processed_patients.append(patient_data)

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1

        previous_page = (
            self._create_paginated_table_url(
                page - 1, facility_id, current_staff_id, None, patient_search
            )
            if has_previous
            else None
        )
        next_page = (
            self._create_paginated_table_url(
                page + 1, facility_id, current_staff_id, None, patient_search
            )
            if has_next
            else None
        )

        context = {
            "patients": processed_patients,
            "staff": staff,
            "facility": facility,
            "current_staff": current_staff,
            "patient_search": patient_search,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": has_next,
                "has_previous": has_previous,
                "next_page": next_page,
                "previous_page": previous_page,
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
        return Staff.objects.filter(active=True).values(
            "id",
            "first_name",
            "last_name",
        )

    def _get_last_visit(self, patient):
        return (
            patient.notes.filter(
                note_type_version__category=NoteTypeCategories.ENCOUNTER,
            )
            .exclude(
                Q(current_state__state=NoteStates.DELETED)
                | Q(current_state__state=NoteStates.CANCELLED)
            )
            .order_by("-datetime_of_service")
            .first()
        )

    def _get_patients_tasks(self, patient) -> dict[str, int]:
        return Task.objects.filter(patient=patient).aggregate(
            all=Count("id"), open=Count("id", filter=Q(status=TaskStatus.OPEN))
        )

    def _get_gaps(self, patient):
        """Get gaps in care for a patient."""
        result = ProtocolCurrent.objects.filter(
            patient=patient,
            status__in=[
                ProtocolResultStatus.STATUS_DUE,
                ProtocolResultStatus.STATUS_SATISFIED,
                ProtocolResultStatus.STATUS_PENDING,
            ]
        ).aggregate(
            gaps=Count('id', filter=Q(status=ProtocolResultStatus.STATUS_DUE)),
            total=Count('id')
        )

        return result.get("gaps", 0), result.get("total", 0)

    def _get_coverage(self, patient) -> str | None:
        """Get coverage information for a patient."""
        coverage = patient.coverages.filter(
            stack=CoverageStack.IN_USE,
        )

        return coverage.last().issuer.name if coverage.exists() else None

    def _get_secrets(self):
        """Get secrets for the dashboard."""
        page_size = self.secrets.get("PAGE_SIZE")
        visit_threshold = self.secrets.get("VISIT_THRESHOLD")
        insurances_logos = self.secrets.get("INSURANCES", {})

        log.info(f"Secrets - Page Size: {page_size}, Visit Threshold: {visit_threshold}")

        return {
            "page_size": self.DEFAULT_PAGE_SIZE if not page_size else int(page_size),
            "visit_threshold": visit_threshold if visit_threshold else self.DEFAULT_VISIT_THRESHOLD,
            "insurances_logos": insurances_logos,
        }

    @property
    def _current_logged_staff(self):
        """Get the currently logged staff member."""
        logged_in_user = Staff.objects.values("first_name", "last_name").get(
            id=self.request.headers["canvas-logged-in-user-id"]
        )

        return {
            "first_name": logged_in_user["first_name"],
            "last_name": logged_in_user["last_name"],
        }

    @property
    def _page_size(self) -> int:
        """Get the page size for pagination."""
        return int(self._get_secrets().get("page_size", self.DEFAULT_PAGE_SIZE))

    def _get_staff_role_for_last_visit(self, patient, provider):
        return (
            CareTeamMembership.objects.filter(
                patient=patient,
                staff=provider,
                status=CareTeamMembershipStatus.ACTIVE,
            )
            .values_list("role__display", flat=True)
            .first()
        )

    # Builds the pagination url
    def _create_paginated_table_url(
        self,
        page: int,
        facility_id: str | None,
        staff_id: str | None,
        facility_search: str | None,
        patient_search: str | None,
    ) -> str:
        """Get the URL for the next page of results."""
        url = "/plugin-io/api/panel_management_dashboard_app/app/table"
        query_params = {
            "page": page,
            "facility_id": facility_id,
            "staff_id": staff_id,
            "facility_search": facility_search,
            "patient_search": patient_search,
        }
        # Remove None values from query_params
        query_params = {k: v for k, v in query_params.items() if v is not None}
        return f"{url}?{urlencode(query_params)}"

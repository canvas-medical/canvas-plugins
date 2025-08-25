from http import HTTPStatus

import arrow
from django.db.models import Q

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api
from canvas_sdk.handlers.simple_api.security import StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus
from canvas_sdk.v1.data.coverage import CoverageStack
from canvas_sdk.v1.data.facility import Facility
from canvas_sdk.v1.data.note import NoteTypeCategories
from canvas_sdk.v1.data.protocol_current import ProtocolCurrent
from canvas_sdk.v1.data.protocol_result import ProtocolResultStatus
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
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        context = {
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
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
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])
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
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
            "facilities": facilities,
            "selected_facility": selected_facility,
            "facility_search": facility_search,
            "page": int(self.request.query_params.get("page", 1)),
            "limit": int(self.request.query_params.get("limit", 10)),
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
        limit = min(int(self.request.query_params.get("limit", 10)), 10)

        # Search query
        patient_search = self.request.query_params.get("patient_search", "").strip()
        log.info(f"Patient search query: {patient_search}")

        # Facilities
        facility_id = self.request.query_params.get("facility_id")
        facility = Facility.objects.get(id=facility_id) if facility_id else None

        # Staff
        staff = self._get_staff()
        current_staff_id = self.request.query_params.get("staff_id")
        current_staff = [member for member in staff if member["id"] == current_staff_id][0] if current_staff_id else None

        # Secrets
        secrets = self._get_secrets()

        # Calculate offset
        offset = (page - 1) * limit

        # Get patients with prefetched relationships
        patients_query = Patient.objects.prefetch_related(
            "telecom",
            "addresses",
            "photos",
            "notes",
            "notes__provider",
            "notes__note_type_version",
        )

        if facility_id:
            patients_query = patients_query.filter(addresses__patientfacilityaddress__facility__id=facility_id)

        if current_staff_id:
            patients_query = patients_query.filter(notes__provider__id=current_staff_id)

        if patient_search:
            patients_query = patients_query.filter(
                Q(first_name__icontains=patient_search) | Q(last_name__icontains=patient_search),
            )

        patients_query = patients_query.distinct()

        # Get total count for pagination info
        total_count = patients_query.count()
        # Apply pagination
        patients_page = patients_query[offset : offset + limit]

        processed_patients = []
        for patient in patients_page:
            last_visit = self._get_last_visit(patient)
            last_visit_staff = (
                [member for member in staff if member["id"] == last_visit.provider.id]
                if last_visit and last_visit.provider
                else None
            )

            gaps, total_gaps = self._get_gaps(patient)

            # Create patient data object
            patient_data = {
                "id": patient.id,
                "photo_url": patient.photo_url,
                "name": patient.preferred_full_name,
                "age": int(patient.age_at(arrow.now())),
                "gender": patient.sex_at_birth,
                "telecom": patient.telecom.first().value if patient.telecom.exists() else None,
                "last_visit": last_visit.datetime_of_service if last_visit else None,
                "provider": last_visit_staff[0] if last_visit_staff else None,
                "tasks": self._get_patients_tasks(patient),
                "gaps": {
                    "due": gaps,
                    "total": total_gaps,
                },
                "insurance": self._get_coverage(patient, last_visit.datetime_of_service if last_visit else None),
                "insurances": secrets.get("insurances_logos"),
                "sticky_note": "",
            }
            processed_patients.append(patient_data)

        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_previous = page > 1

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
        care_team = (
            CareTeamMembership.objects.values(
                "staff__id",
                "staff__first_name",
                "staff__last_name",
                "role__display",
            )
            .filter(
                status=CareTeamMembershipStatus.ACTIVE,
            )
            .distinct()
        )

        return [
            {
                "id": member["staff__id"],
                "first_name": member["staff__first_name"],
                "last_name": member["staff__last_name"],
                "role": member["role__display"],
            }
            for member in care_team
        ] if care_team else []

    def _get_last_visit(self, patient):
        query = patient.notes.filter(
            note_type_version__category=NoteTypeCategories.ENCOUNTER,
        ).order_by("-datetime_of_service")

        return query.first() if query.exists() else None

    def _get_patients_tasks(self, patient) -> dict[str, int]:
        return {
            "all": Task.objects.filter(patient=patient).count(),
            "open": Task.objects.filter(
                patient=patient,
                status=TaskStatus.OPEN,
            ).count(),
        }

    def _get_gaps(self, patient):
        """Get gaps in care for a patient."""
        gaps = ProtocolCurrent.objects.filter(
            patient=patient,
            status=ProtocolResultStatus.STATUS_DUE,
        ).count()

        total_gaps = ProtocolCurrent.objects.filter(
            patient=patient,
            status__in=[
                ProtocolResultStatus.STATUS_DUE,
                ProtocolResultStatus.STATUS_SATISFIED,
                ProtocolResultStatus.STATUS_PENDING,
            ],
        ).count()

        return (gaps, total_gaps) if total_gaps > 0 else (0, 0)

    def _get_coverage(self, patient, last_visit_date=None) -> str | None:
        """Get coverage information for a patient."""
        coverage = patient.coverages.filter(
            stack=CoverageStack.IN_USE,
        )

        return coverage.last().issuer.name if coverage.exists() else None

    def _get_secrets(self):
        """Get secrets for the dashboard."""
        page_size = self.secrets.get('PAGE_SIZE', 10)
        visit_threshold = self.secrets.get('VISIT_THRESHOLD', '1 day')
        insurances_logos = self.secrets.get('INSURANCES', {})

        return {
            "page_size": page_size,
            "visit_threshold": visit_threshold,
            "insurances_logos": insurances_logos,
        }

    # @api.get("/facilities/<facility_id>/patients")
    # def get_facility_patients(self) -> list[Response | Effect]:
    #     """Serve the patients for a specific facility."""
    #     facility_id = self.request.path_params.get("facility_id")
    #     page = int(self.request.query_params.get("page", 1))
    #     limit = min(int(self.request.query_params.get("limit", 10)), 10)
    #     offset = (page - 1) * limit

    #     facility = Facility.objects.get(id=facility_id)
    #     total = facility.patient_facilities.count()
    #     patients = [f.patient for f in list(facility.patient_facilities.all())[offset:offset + limit]]
    #     context = {
    #         "patients": patients,
    #         "page": page,
    #         "limit": limit,
    #         "total": total,
    #     }

    #     return [
    #         Response(
    #             render_to_string("static/table.html", context).encode(),
    #             status_code=HTTPStatus.OK,
    #         )
    #     ]
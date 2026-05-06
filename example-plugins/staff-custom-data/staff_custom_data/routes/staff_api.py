from http import HTTPStatus

from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from canvas_sdk.v1.data import PluginData
from logger import log


class StaffDataAPI(SimpleAPI):
    """API for managing extended staff profile data.

    Schema:
        - biography: str - Staff member's bio
        - specialties: list[str] - Medical specialties (e.g., ["Cardiology", "Internal Medicine"])
        - languages: list[str] - Languages spoken (e.g., ["English", "Spanish"])
        - years_of_experience: int - Years in practice
        - accepting_new_patients: bool - Currently accepting new patients

    Filtering (GET /staff/):
        - specialty: Filter by specialty (case-sensitive, exact match)
        - language: Filter by language (case-sensitive, exact match)
        - accepting_new_patients: Filter by availability (true/false)
        - min_experience: Minimum years of experience
    """

    PREFIX = "/staff"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow all requests (demo purposes)."""
        return True

    def _serialize_record(self, record: PluginData) -> dict:
        """Convert a PluginData record to API response format."""
        staff_uuid = record.key.replace("staff:", "")
        return {
            "staff_uuid": staff_uuid,
            "biography": record.data.get("biography", ""),
            "specialties": record.data.get("specialties", []),
            "languages": record.data.get("languages", []),
            "years_of_experience": record.data.get("years_of_experience"),
            "accepting_new_patients": record.data.get("accepting_new_patients"),
        }

    @api.get("/")
    def list_all(self) -> list[Response]:
        """Get all staff data with optional filtering (all DB-level)."""
        params = self.request.query_params

        # Build ORM query and log string
        filters = ['key__startswith="staff:"']
        queryset = PluginData.objects.filter(key__startswith="staff:")

        # Boolean filter
        if accepting := params.get("accepting_new_patients"):
            value = accepting.lower() == "true"
            queryset = queryset.filter(data__accepting_new_patients=value)
            filters.append(f"data__accepting_new_patients={value}")

        # Integer comparison
        if min_exp := params.get("min_experience"):
            queryset = queryset.filter(data__years_of_experience__gte=int(min_exp))
            filters.append(f"data__years_of_experience__gte={int(min_exp)}")

        # Array contains (case-sensitive, exact match)
        if specialty := params.get("specialty"):
            queryset = queryset.filter(data__specialties__contains=[specialty])
            filters.append(f'data__specialties__contains=["{specialty}"]')

        if language := params.get("language"):
            queryset = queryset.filter(data__languages__contains=[language])
            filters.append(f'data__languages__contains=["{language}"]')

        # Log ORM query for shell_plus
        orm_query = f"PluginData.objects.filter({', '.join(filters)})"
        log.info(f"\n{'=' * 60}\nORM QUERY:\n{orm_query}\n{'=' * 60}\n")

        result = [self._serialize_record(record) for record in queryset]
        return [JSONResponse({"staff": result, "count": len(result)})]

    @api.get("/<uuid>/")
    def get_one(self) -> list[Response]:
        """Get data for a single staff member."""
        staff_uuid = self.request.path_params.get("uuid")
        record = PluginData.objects.filter(key=f"staff:{staff_uuid}").first()

        if not record:
            return [
                JSONResponse(
                    {"error": "Staff data not found"},
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        return [JSONResponse(self._serialize_record(record))]

    @api.put("/<uuid>/")
    def update(self) -> list[Response]:
        """Update staff profile data (merges with existing data)."""
        staff_uuid = self.request.path_params.get("uuid")

        # Validate staff exists
        # if not Staff.objects.filter(id=staff_uuid).exists():
        #     return [JSONResponse(
        #         {"error": "Staff member not found"},
        #         status_code=HTTPStatus.NOT_FOUND,
        #     )]

        body = self.request.json()
        data = {}

        # Validate and collect fields
        if "biography" in body:
            if not isinstance(body["biography"], str):
                return [
                    JSONResponse(
                        {"error": "biography must be a string"},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                ]
            data["biography"] = body["biography"]

        if "specialties" in body:
            if not isinstance(body["specialties"], list):
                return [
                    JSONResponse(
                        {"error": "specialties must be a list of strings"},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                ]
            data["specialties"] = body["specialties"]

        if "languages" in body:
            if not isinstance(body["languages"], list):
                return [
                    JSONResponse(
                        {"error": "languages must be a list of strings"},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                ]
            data["languages"] = body["languages"]

        if "years_of_experience" in body:
            if not isinstance(body["years_of_experience"], int):
                return [
                    JSONResponse(
                        {"error": "years_of_experience must be an integer"},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                ]
            data["years_of_experience"] = body["years_of_experience"]

        if "accepting_new_patients" in body:
            if not isinstance(body["accepting_new_patients"], bool):
                return [
                    JSONResponse(
                        {"error": "accepting_new_patients must be a boolean"},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                ]
            data["accepting_new_patients"] = body["accepting_new_patients"]

        if not data:
            return [
                JSONResponse(
                    {"error": "No valid fields provided"},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

        # Upsert merges with existing data
        record = PluginData.objects.upsert(key=f"staff:{staff_uuid}", data=data)

        return [
            JSONResponse(
                {
                    "message": "Staff data updated",
                    **self._serialize_record(record),
                }
            )
        ]

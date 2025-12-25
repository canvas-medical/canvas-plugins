"""
Specialty Report Template API Handler.

This module provides a Simple API endpoint for querying SpecialtyReportTemplate,
SpecialtyReportTemplateField, and SpecialtyReportTemplateFieldOption SDK models.
"""

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from canvas_sdk.v1.data import SpecialtyReportTemplate
from logger import log

# Constants
MAX_RESULTS = 20
QUERY_PARAM_TRUE = "true"
QUERY_PARAM_FALSE = "false"
DEFAULT_INCLUDE_FIELDS = "false"
DEFAULT_INCLUDE_OPTIONS = "false"


class SpecialtyReportTemplateAPI(SimpleAPIRoute):
    """
    Simple API endpoint to query and return SpecialtyReportTemplate data with fields and options.

    Supports the following query parameters:

    - active: Filter active templates (true)
    - search: Full-text search query
    - custom: Filter custom (true) or builtin (false) templates
    - specialty_code: Filter by specialty taxonomy code (e.g., "207RC0000X")
    - include_fields: Include field details (true/false, default false)
    - include_options: Include field options (true/false, default false, requires include_fields=true)

    Example usage:

        GET /specialty-report-templates
        GET /specialty-report-templates?active=true
        GET /specialty-report-templates?search=cardiology
        GET /specialty-report-templates?specialty_code=207RC0000X
        GET /specialty-report-templates?active=true&custom=false
        GET /specialty-report-templates?include_fields=true
        GET /specialty-report-templates?include_fields=true&include_options=true
    """

    PATH = "/specialty-report-templates"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow unauthenticated access for testing."""
        log.info("SpecialtyReportTemplateAPI.authenticate() called")
        return True

    def get(self) -> list[JSONResponse]:
        """Handle GET requests to list and filter specialty report templates."""
        log.info("SpecialtyReportTemplateAPI.get() called")
        log.info(f"Request path: {self.request.path}")
        log.info(f"Request path_params: {self.request.path_params}")
        log.info(f"Request query_params: {self.request.query_params}")

        try:
            params = self._extract_query_params()
            templates = self._build_queryset(params)
            result = [
                self._build_template_data(
                    template, params["include_fields"], params["include_options"]
                )
                for template in templates[:MAX_RESULTS]
            ]
            return self._build_response(result)
        except Exception as e:
            log.error(f"Error processing request: {e}", exc_info=True)
            return [JSONResponse({"error": str(e)}, status_code=500)]

    # Private Helper Methods

    def _extract_query_params(self) -> dict:
        """Extract and parse query parameters from request.

        Returns:
            dict: Dictionary containing parsed query parameters with keys:
                - active: str | None - Active filter value
                - search: str | None - Search query string
                - custom: str | None - Custom filter value
                - specialty_code: str | None - Specialty code filter
                - include_fields: bool - Whether to include fields
                - include_options: bool - Whether to include options
        """
        query_params = self.request.query_params
        include_fields = (
            query_params.get("include_fields", DEFAULT_INCLUDE_FIELDS) == QUERY_PARAM_TRUE
        )
        include_options = (
            query_params.get("include_options", DEFAULT_INCLUDE_OPTIONS) == QUERY_PARAM_TRUE
        )

        log.info(
            f"Filters - active: {query_params.get('active')}, search: {query_params.get('search')}, "
            f"custom: {query_params.get('custom')}, specialty_code: {query_params.get('specialty_code')}, "
            f"include_fields: {include_fields}, include_options: {include_options}"
        )

        return {
            "active": query_params.get("active"),
            "search": query_params.get("search"),
            "custom": query_params.get("custom"),
            "specialty_code": query_params.get("specialty_code"),
            "include_fields": include_fields,
            "include_options": include_options,
        }

    def _build_queryset(self, params: dict):
        """Build and filter queryset based on query parameters.

        Args:
            params: Dictionary of query parameters from _extract_query_params()

        Returns:
            QuerySet: Filtered queryset of SpecialtyReportTemplate objects

        Note:
            When include_fields is True, prefetch_related is used which may return
            list-like objects instead of QuerySets for related fields.
        """
        log.info("Querying SpecialtyReportTemplate...")
        templates = SpecialtyReportTemplate.objects.all()
        log.info("Initial queryset created")

        if params["active"] == QUERY_PARAM_TRUE:
            templates = templates.active()

        if params["search"]:
            templates = templates.search(params["search"])

        if params["custom"] == QUERY_PARAM_TRUE:
            templates = templates.custom()
        elif params["custom"] == QUERY_PARAM_FALSE:
            templates = templates.builtin()

        if params["specialty_code"]:
            templates = templates.by_specialty(params["specialty_code"])

        if params["include_fields"]:
            templates = templates.prefetch_related("fields", "fields__options")

        log.info("Queryset built with filters")
        return templates

    def _build_template_data(
        self, template: SpecialtyReportTemplate, include_fields: bool, include_options: bool
    ) -> dict:
        """Build template data dictionary for response.

        Args:
            template: SpecialtyReportTemplate instance
            include_fields: Whether to include fields in response
            include_options: Whether to include options in fields (requires include_fields=True)

        Returns:
            dict: Template data dictionary with all template fields and optionally fields/options
        """
        template_data = {
            "dbid": template.dbid,
            "name": template.name,
            "code": template.code,
            "code_system": template.code_system,
            "search_keywords": template.search_keywords,
            "active": template.active,
            "custom": template.custom,
            "search_as": template.search_as,
            "specialty_name": template.specialty_name,
            "specialty_code": template.specialty_code,
            "specialty_code_system": template.specialty_code_system,
        }

        if include_fields:
            fields = template.fields.all()
            template_data["field_count"] = len(fields)
            template_data["fields"] = self._build_fields_data(fields, include_options)

        return template_data

    def _build_fields_data(self, fields, include_options: bool) -> list[dict]:
        """Build fields array with optional options.

        Args:
            fields: QuerySet or list of SpecialtyReportTemplateField objects
            include_options: Whether to include options for each field

        Returns:
            list[dict]: List of field dictionaries, each containing field data and optionally options

        Note:
            Fields are sorted by sequence. When using prefetch_related, fields may be a list
            instead of a QuerySet, so we handle both cases.
        """
        sorted_fields = self._sort_fields_by_sequence(fields)
        return [self._build_field_dict(field, include_options) for field in sorted_fields]

    def _build_field_dict(self, field, include_options: bool) -> dict:
        """Build dictionary for a single field.

        Args:
            field: SpecialtyReportTemplateField instance
            include_options: Whether to include options for this field

        Returns:
            dict: Field dictionary with field data and optionally options
        """
        field_dict = {
            "dbid": field.dbid,
            "sequence": field.sequence,
            "code": field.code,
            "code_system": field.code_system,
            "label": field.label,
            "units": field.units,
            "type": field.type,
            "required": field.required,
        }

        if include_options:
            options = field.options.all()
            field_dict["options"] = self._build_options_data(options)
            field_dict["option_count"] = len(field_dict["options"])

        return field_dict

    def _build_options_data(self, options) -> list[dict]:
        """Build options array for a field.

        Args:
            options: QuerySet or list of SpecialtyReportTemplateFieldOption objects

        Returns:
            list[dict]: List of option dictionaries, each containing dbid, label, and key
        """
        return [
            {
                "dbid": option.dbid,
                "label": option.label,
                "key": option.key,
            }
            for option in options
        ]

    def _sort_fields_by_sequence(self, fields) -> list:
        """Sort fields by sequence, handling both QuerySet and list types.

        Args:
            fields: QuerySet or list of SpecialtyReportTemplateField objects

        Returns:
            list: Sorted list of fields ordered by sequence

        Note:
            When using prefetch_related, Django may return a list instead of a QuerySet.
            This method handles both cases.
        """
        if hasattr(fields, "order_by"):
            return list(fields.order_by("sequence"))
        return sorted(fields, key=lambda f: f.sequence)

    def _build_response(self, templates: list[dict]) -> list[JSONResponse]:
        """Build final JSONResponse with template data.

        Args:
            templates: List of template dictionaries

        Returns:
            list[JSONResponse]: List containing single JSONResponse with count and templates
        """
        return [
            JSONResponse(
                {
                    "count": len(templates),
                    "templates": templates,
                }
            )
        ]

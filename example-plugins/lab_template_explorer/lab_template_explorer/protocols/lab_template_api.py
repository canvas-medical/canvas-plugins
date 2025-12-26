from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.events import EventType
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import LabReportTemplate
from logger import log


class LabTemplateAPI(SimpleAPIRoute):
    """
    Simple API endpoint to query and return LabReportTemplate data.

    Supports path parameter:
    - patient_id: Patient ID (required in path)

    Supports the following query parameters:
    - search: Search templates by name or keywords
    - active: Filter to active templates only (true/false)
    - inactive: Filter to inactive templates only (true/false)
    - poc: Filter to point-of-care templates only (true/false)
    - custom: Filter to custom templates only (true/false)
    - builtin: Filter to built-in templates only (true/false)

    Example usage:
        GET /lab-templates/<patient_id>
        GET /lab-templates/<patient_id>?search=glucose
        GET /lab-templates/<patient_id>?active=true
        GET /lab-templates/<patient_id>?active=true&poc=true
    """

    PATH = "/lab-templates/<patient_id>"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow unauthenticated access for testing."""
        log.info("LabTemplateAPI.authenticate() called")
        return True

    def get(self) -> list[JSONResponse]:
        """Handle GET requests to list and filter lab report templates."""
        log.info("LabTemplateAPI.get() called")
        log.info(f"Request path: {self.request.path}")
        log.info(f"Request path_params: {self.request.path_params}")
        log.info(f"Request query_params: {self.request.query_params}")

        # Extract path parameter
        patient_id = self.request.path_params.get("patient_id")
        log.info(f"Patient ID: {patient_id}")

        # Extract query parameters
        search_query = self.request.query_params.get("search")
        active_only = self.request.query_params.get("active") == "true"
        inactive_only = self.request.query_params.get("inactive") == "true"
        poc_only = self.request.query_params.get("poc") == "true"
        custom_only = self.request.query_params.get("custom") == "true"
        builtin_only = self.request.query_params.get("builtin") == "true"
        log.info(
            f"Filters - search: {search_query}, active: {active_only}, "
            f"inactive: {inactive_only}, poc: {poc_only}, "
            f"custom: {custom_only}, builtin: {builtin_only}"
        )

        # Build queryset using SDK QuerySet methods
        log.info("Querying LabReportTemplate...")
        try:
            templates = LabReportTemplate.objects.all()
            log.info("Initial queryset created")

            if active_only:
                templates = templates.active()
            if inactive_only:
                templates = templates.inactive()
            if poc_only:
                templates = templates.point_of_care()
            if custom_only:
                templates = templates.custom()
            if builtin_only:
                templates = templates.builtin()
            if search_query:
                templates = templates.search(search_query)

            # Prefetch related fields and options for efficient querying
            templates = templates.prefetch_related("fields", "fields__options")
            log.info("Queryset built with prefetch")
        except Exception as e:
            log.error(f"Error building queryset: {e}")
            return [JSONResponse({"error": str(e)}, status_code=500)]

        # Build response with template details
        result = []
        for template in templates[:20]:  # Limit to 20 results
            template_data = {
                "dbid": template.dbid,
                "id": str(template.id),
                "name": template.name,
                "code": template.code,
                "code_system": template.code_system,
                "search_keywords": template.search_keywords,
                "active": template.active,
                "custom": template.custom,
                "poc": template.poc,
                "fields": [
                    {
                        "dbid": field.dbid,
                        "label": field.label,
                        "code": field.code,
                        "code_system": field.code_system,
                        "units": field.units,
                        "field_type": field.field_type,
                        "required": field.required,
                        "sequence": field.sequence,
                        "options": [
                            {"label": opt.label, "key": opt.key} for opt in field.options.all()
                        ],
                    }
                    for field in template.fields.all()
                ],
            }
            result.append(template_data)

        return [
            JSONResponse(
                {
                    "patient_id": patient_id,
                    "count": len(result),
                    "templates": result,
                }
            )
        ]


class LabTemplateProtocolCard(BaseProtocol):
    """
    Protocol that displays lab template statistics as a protocol card.

    This protocol responds to patient chart summary events and displays
    a summary of available lab report templates including:
    - Total count of templates
    - Count of active, inactive, POC, custom, and built-in templates
    - List of top templates
    """

    RESPONDS_TO = EventType.Name(EventType.PATIENT_CHART_SUMMARY__SECTION_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Compute the protocol card with template statistics."""
        patient_id = self.target

        # Query template statistics using SDK QuerySet methods
        total = LabReportTemplate.objects.count()
        active = LabReportTemplate.objects.active().count()
        inactive = LabReportTemplate.objects.inactive().count()
        poc = LabReportTemplate.objects.point_of_care().count()
        custom = LabReportTemplate.objects.custom().count()
        builtin = LabReportTemplate.objects.builtin().count()

        # Get sample templates
        sample_templates = list(LabReportTemplate.objects.active().prefetch_related("fields")[:5])

        # Build narrative text
        if sample_templates:
            template_list = "\n".join(
                [f"  - {t.name} ({t.fields.count()} fields)" for t in sample_templates]
            )
        else:
            template_list = "  No templates available"

        narrative = f"""
        Lab Report Templates Summary:

        Total Templates: {total}
        Active: {active}
        Inactive: {inactive}
        Point-of-Care: {poc}
        Custom: {custom}
        Built-in: {builtin}

        Sample Templates:
        {template_list}
        """

        # Create and return protocol card
        card = ProtocolCard(
            patient_id=patient_id,
            key="lab-template-explorer",
            title="Lab Report Templates",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
        )

        return [card.apply()]

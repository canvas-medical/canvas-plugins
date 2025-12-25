from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.events import EventType
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import ImagingReportTemplate
from logger import log


class ImagingTemplateAPI(SimpleAPIRoute):
    """
    Simple API endpoint to query and return ImagingReportTemplate data.

    Supports path parameter:
    - patient_id: Patient ID (required in path)

    Supports the following query parameters:
    - search: Search templates by keywords
    - active: Filter to active templates only (true/false)
    - custom: Filter to custom templates only (true/false)
    - builtin: Filter to built-in templates only (true/false)

    Example usage:
        GET /imaging-templates/<patient_id>
        GET /imaging-templates/<patient_id>?search=MRI
        GET /imaging-templates/<patient_id>?active=true
        GET /imaging-templates/<patient_id>?active=true&custom=true
    """

    PATH = "/imaging-templates/<patient_id>"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow unauthenticated access for testing."""
        log.info("ImagingTemplateAPI.authenticate() called")
        return True

    def get(self) -> list[JSONResponse]:
        """Handle GET requests to list and filter imaging report templates."""
        log.info("ImagingTemplateAPI.get() called")
        log.info(f"Request path: {self.request.path}")
        log.info(f"Request path_params: {self.request.path_params}")
        log.info(f"Request query_params: {self.request.query_params}")

        # Extract path parameter
        patient_id = self.request.path_params.get("patient_id")
        log.info(f"Patient ID: {patient_id}")

        # Extract query parameters
        search_query = self.request.query_params.get("search")
        active_only = self.request.query_params.get("active") == "true"
        custom_only = self.request.query_params.get("custom") == "true"
        builtin_only = self.request.query_params.get("builtin") == "true"
        log.info(
            f"Filters - search: {search_query}, active: {active_only}, custom: {custom_only}, builtin: {builtin_only}"
        )

        # Build queryset using SDK QuerySet methods
        log.info("Querying ImagingReportTemplate...")
        try:
            templates = ImagingReportTemplate.objects.all()
            log.info("Initial queryset created")

            if active_only:
                templates = templates.active()
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
                "long_name": template.long_name,
                "code": template.code,
                "code_system": template.code_system,
                "active": template.active,
                "custom": template.custom,
                "rank": template.rank,
                "fields": [
                    {
                        "dbid": field.dbid,
                        "label": field.label,
                        "code": field.code,
                        "type": field.type,
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


class ImagingTemplateProtocolCard(BaseProtocol):
    """
    Protocol that displays imaging template statistics as a protocol card.

    This protocol responds to patient chart summary events and displays
    a summary of available imaging report templates including:
    - Total count of templates
    - Count of active, custom, and built-in templates
    - List of top templates by rank
    """

    RESPONDS_TO = EventType.Name(EventType.PATIENT_CHART_SUMMARY__SECTION_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Compute the protocol card with template statistics."""
        patient_id = self.target

        # Query template statistics using SDK QuerySet methods
        total = ImagingReportTemplate.objects.count()
        active = ImagingReportTemplate.objects.active().count()
        custom = ImagingReportTemplate.objects.custom().count()
        builtin = ImagingReportTemplate.objects.builtin().count()

        # Get sample templates ordered by rank
        sample_templates = list(
            ImagingReportTemplate.objects.active().prefetch_related("fields").order_by("rank")[:5]
        )

        # Build narrative text
        if sample_templates:
            template_list = "\n".join(
                [f"  - {t.name} ({t.fields.count()} fields)" for t in sample_templates]
            )
        else:
            template_list = "  No templates available"

        narrative = f"""
        Imaging Report Templates Summary:

        Total Templates: {total}
        Active: {active}
        Custom: {custom}
        Built-in: {builtin}

        Top Templates by Rank:
        {template_list}
        """

        # Create and return protocol card
        card = ProtocolCard(
            patient_id=patient_id,
            key="imaging-template-explorer",
            title="Imaging Report Templates",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
        )

        return [card.apply()]

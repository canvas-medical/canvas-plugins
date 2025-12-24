from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from canvas_sdk.v1.data import IntegrationTask, IntegrationTaskReview
from logger import log


class IntegrationTaskAPI(SimpleAPIRoute):
    """
    Simple API endpoint to query and return IntegrationTask data with reviews.

    Supports path parameter:
    - patient_id: Patient ID (required in path)

    Supports the following query parameters:
    - status: Filter by status (unread, pending_review, processed, errors, junked)
    - channel: Filter by channel (fax, uploads, integration_engine, patient_portal)
    - include_reviews: Include review details (true/false, default true)

    Example usage:
        GET /integration-tasks/<patient_id>
        GET /integration-tasks/<patient_id>?status=unread
        GET /integration-tasks/<patient_id>?channel=fax
        GET /integration-tasks/<patient_id>?status=pending_review&channel=fax
        GET /integration-tasks/<patient_id>?include_reviews=false
    """

    PATH = "/integration-tasks/<patient_id>"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow unauthenticated access for testing."""
        log.info("IntegrationTaskAPI.authenticate() called")
        return True

    def get(self) -> list[Response | Effect]:
        """Handle GET requests to list and filter integration tasks."""
        log.info("IntegrationTaskAPI.get() called")
        log.info(f"Request path: {self.request.path}")
        log.info(f"Request path_params: {self.request.path_params}")
        log.info(f"Request query_params: {self.request.query_params}")

        # Extract path parameter
        patient_id = self.request.path_params.get("patient_id")
        log.info(f"Patient ID: {patient_id}")

        # Extract query parameters
        status_filter = self.request.query_params.get("status")
        channel_filter = self.request.query_params.get("channel")
        include_reviews = self.request.query_params.get("include_reviews", "true") == "true"
        log.info(
            f"Filters - status: {status_filter}, channel: {channel_filter}, include_reviews: {include_reviews}"
        )

        # Build queryset using SDK QuerySet methods
        log.info("Querying IntegrationTask...")
        try:
            tasks = IntegrationTask.objects.all()
            log.info("Initial queryset created")

            # Filter by patient if provided
            if patient_id and patient_id != "all":
                tasks = tasks.for_patient(patient_id)

            # Apply status filters
            if status_filter == "unread":
                tasks = tasks.unread()
            elif status_filter == "pending_review":
                tasks = tasks.pending_review()
            elif status_filter == "processed":
                tasks = tasks.processed()
            elif status_filter == "errors":
                tasks = tasks.with_errors()
            elif status_filter == "junked":
                tasks = tasks.junked()
            elif status_filter == "not_junked":
                tasks = tasks.not_junked()

            # Apply channel filters
            if channel_filter == "fax":
                tasks = tasks.faxes()
            elif channel_filter == "uploads":
                tasks = tasks.uploads()
            elif channel_filter == "integration_engine":
                tasks = tasks.from_integration_engine()
            elif channel_filter == "patient_portal":
                tasks = tasks.from_patient_portal()

            # Prefetch related patient for efficient access
            tasks = tasks.select_related("patient", "service_provider")

            log.info("Queryset built with filters")
        except Exception as e:
            log.error(f"Error building queryset: {e}")
            return [JSONResponse({"error": str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

        # Build response with task details
        result = []
        for task in tasks[:20]:  # Limit to 20 results
            task_data = {
                "id": str(task.id),
                "status": task.status,
                "type": task.type,
                "title": task.title,
                "channel": task.channel,
                # Use patient.id (UUID) not patient_id (FK integer)
                "patient_id": task.patient.id if task.patient else None,
                "service_provider_id": task.service_provider.id if task.service_provider else None,
                "is_fax": task.is_fax,
                "is_pending": task.is_pending,
                "is_processed": task.is_processed,
                "has_error": task.has_error,
                "is_junked": task.is_junked,
                "created": str(task.created) if hasattr(task, "created") else None,
                "modified": str(task.modified) if hasattr(task, "modified") else None,
            }

            # Include reviews if requested
            if include_reviews:
                reviews = IntegrationTaskReview.objects.for_task(str(task.id)).active()
                task_data["reviews"] = [
                    {
                        "id": str(review.id),
                        "template_name": review.template_name,
                        "document_key": review.document_key,
                        "reviewer_id": review.reviewer_id,
                        "team_reviewer_id": review.team_reviewer_id,
                        "junked": review.junked,
                        "is_active": review.is_active,
                        "created": str(review.created) if hasattr(review, "created") else None,
                        "modified": str(review.modified) if hasattr(review, "modified") else None,
                    }
                    for review in reviews
                ]
                task_data["review_count"] = len(task_data["reviews"])

            result.append(task_data)

        return [
            JSONResponse(
                {
                    "patient_id": patient_id,
                    "count": len(result),
                    "tasks": result,
                }
            )
        ]

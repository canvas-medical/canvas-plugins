import arrow

from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.effects.task import AddTask
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute

#
# POST /plugin-io/api/task_completion_protocol_updater/create-test-protocol
# Body: { "patient_id": "valid patient ID" }
# Headers: "Authorization <your value for 'api-key'>"
#


class CreateTestProtocolAPI(SimpleAPIRoute):
    """Create a test protocol card and task for testing purposes."""

    PATH = "/create-test-protocol"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Check if the provided API key matches the secret."""
        return credentials.key == self.secrets["api-key"]

    def post(self) -> list[Response]:
        """Create a test protocol card and an associated task on the given patient."""
        patient_id = self.request.json().get("patient_id")

        if not patient_id:
            return [JSONResponse({"error": "patient_id is required"}, status_code=400)]

        key = self.request.json().get("key", f"test_{patient_id}")
        card = ProtocolCard(
            patient_id=patient_id,
            key=key,
            status=ProtocolCard.Status.DUE,
            title=self.request.json().get("title", "Test Protocol Card"),
        )

        # Create labels list explicitly
        task_labels = ["LINKED_PROTOCOL_CARD", f"PROTOCOL_CARD_{key}"]

        add_task = AddTask(
            patient_id=patient_id,
            title="This task is linked to a protocol card.",
            due=arrow.utcnow().shift(days=5).datetime,
        )

        # Set labels explicitly after instantiation
        add_task.labels = task_labels

        return [
            card.apply(),
            add_task.apply(),
            JSONResponse({
                "message": "Protocol card and task created",
            })
        ]

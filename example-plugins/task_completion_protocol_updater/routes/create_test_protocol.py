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
    PATH = "/create-test-protocol"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        return credentials.key == self.secrets["api-key"]

    def post(self) -> list[Response]:
        patient_id = self.request.json().get("patient_id")
        
        if not patient_id:
            return [JSONResponse({"error": "patient_id is required"}, status_code=400)]

        card = ProtocolCard(
            patient_id=patient_id,
            key="annual_exam_2025",
            status=ProtocolCard.Status.DUE,
            title="Annual exam task"
        )

        add_task = AddTask(
            patient_id=patient_id,
            title="Please close out this protocol card.",
            due=arrow.utcnow().shift(days=5).datetime,
            labels=["LINKED_PROTOCOL_CARD", "PROTOCOL_CARD_annual_exam_2025"],
        )

        return [card.apply(), add_task.apply(), JSONResponse({"message": "Protocol card and task created"})]
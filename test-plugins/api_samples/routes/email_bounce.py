import arrow

from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute
from canvas_sdk.v1.data import Patient

#
# POST /plugin-io/api/api_samples/crm-webhooks/email-bounce
# Body: { "mrn": "valid patient MRN" }
# Headers: "Authorization <your value for 'my-api-key'>"
#


class EmailBounceAPI(SimpleAPIRoute):
    PATH = "/crm-webhooks/email-bounce"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        return credentials.key == self.secrets["my-api-key"]

    def post(self) -> list[Response]:
        patient = Patient.objects.get(mrn=self.request.json()["mrn"])
        five_days_from_now = arrow.utcnow().shift(days=5).datetime

        task_effect = AddTask(
            patient_id=patient.id,
            title="Please confirm contact information.",
            due=five_days_from_now,
            status=TaskStatus.OPEN,
            labels=["CRM"],
        )

        return [task_effect.apply(), JSONResponse({"message": "Task Created"})]

from canvas_sdk.effects import Effect
from canvas_sdk.handlers.action_button import ActionButton

from canvas_sdk.clients import CanvasFhir

from logger import log

class Handler(ActionButton):
    """"""

    BUTTON_TITLE = "Trigger FHIR Request"
    BUTTON_KEY = "TRIGGER_FHIR_REQUEST"
    BUTTON_LOCATION = ActionButton.ButtonLocation.CHART_SUMMARY_ALLERGIES_SECTION

    def handle(self) -> list[Effect]:
        """"""

        client_id = self.secrets["CANVAS_FHIR_CLIENT_ID"]
        client_secret = self.secrets["CANVAS_FHIR_CLIENT_SECRET"]
        customer_identifier = self.environment["CUSTOMER_IDENTIFIER"]
        patient_id = self.event.target.id

        log.info(f"--------------------------------")

        client = CanvasFhir(client_id, client_secret, customer_identifier)

        search_response = client.search("AllergyIntolerance", {"patient": f"Patient/{patient_id}"})

        log.info(f"Search: {search_response}")

        read_response = client.read("AllergyIntolerance", search_response["entry"][0]["resource"]["id"])

        log.info(f"Read: {read_response}")

        log.info(f"--------------------------------")

        return []

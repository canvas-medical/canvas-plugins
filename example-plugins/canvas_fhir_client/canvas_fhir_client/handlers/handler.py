from canvas_sdk.clients import CanvasFhir
from canvas_sdk.effects import Effect
from canvas_sdk.handlers.action_button import ActionButton
from logger import log


class Handler(ActionButton):
    """Handler for the FHIR request button."""

    BUTTON_TITLE = "Trigger FHIR Request"
    BUTTON_KEY = "TRIGGER_FHIR_REQUEST"
    BUTTON_LOCATION = ActionButton.ButtonLocation.CHART_SUMMARY_ALLERGIES_SECTION

    def handle(self) -> list[Effect]:
        """Handle the button click."""
        client_id = self.secrets["CANVAS_FHIR_CLIENT_ID"]
        client_secret = self.secrets["CANVAS_FHIR_CLIENT_SECRET"]
        patient_id = self.event.target.id

        log.info("--------------------------------")

        client = CanvasFhir(client_id, client_secret)

        search_response = client.search("AllergyIntolerance", {"patient": f"Patient/{patient_id}"})

        log.info(f"Search: {search_response}")

        read_response = client.read(
            "AllergyIntolerance", search_response["entry"][0]["resource"]["id"]
        )

        log.info(f"Read: {read_response}")

        log.info("--------------------------------")

        return []

import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.v1.data import Command, Note, NoteStateChangeEvent

# Import the helper methods from the API
from fullscript.api.fullscript_api import FullscriptAPI
from logger import log


# TODO: Refactor common methods with my_application.py
def get_application_url(
    params: dict, patient_key: str | None = None, note_id: str | None = None
) -> str:
    """Get the path to the Fullscript application."""
    url = "/plugin-io/api/fullscript/app/fullscript-app"

    if patient_key:
        url += f"?patient={patient_key}"
    for param in params:
        url += f"&{param}={params[param]}"
    if note_id:
        url += f"&noteId={note_id}"

    return url


def handle_treatment_plan(patient_id: str, note_id: str, user_id: str, secrets: dict) -> dict:
    """Create a treatment plan in Fullscript based on the prescribe and refill commands in the note."""
    log.info("!! Fullscript create treatment plan")

    schema_key_commands = ["prescribe", "refill"]

    log.info(f"NOTE_ID {note_id}")

    commands = Command.objects.filter(
        note__id=note_id, schema_key__in=schema_key_commands, committer__isnull=False
    ).all()

    if commands:
        log.info(f"!! Prescribe commands {commands}")
    else:
        log.info("!! No prescribe commands found, skipping Fullscript treatment plan creation")

        return {"success": False, "error": "No prescribe commands found"}

    medications = []

    for command in commands:
        log.info(f"!! Command {command.data}")

        medication = command.data.get("prescribe", {})
        first_coding = medication.get("extra", {}).get("coding", {})[0]
        medication_code = first_coding.get("code", "")
        medication_id = medication_code[len("fullscript-") :]

        recommendation = {
            "variant_id": medication_id,
            "units_to_purchase": command.data.get("quantity_to_dispense", ""),
            "refill": command.data.get("refills", ""),
            "dosage": {
                "duration": command.data.get("days_supply", ""),
                "additional_info": command.data.get("sig", ""),
                "format": command.data.get("type_to_dispense", {}).get("text", ""),
            },
        }

        medications.append(recommendation)

    log.info(f"!! Medications for treatment plan: {json.dumps(medications)}")

    if not user_id:
        log.warning("!! No user_id available, skipping Fullscript search")

        return {"success": False, "error": "Missing user_id"}

    # Get valid access token (handles refresh if needed)
    client_id = secrets["FULLSCRIPT_CLIENT_ID"]
    client_secret = secrets["FULLSCRIPT_CLIENT_SECRET"]

    token_result = FullscriptAPI.get_valid_access_token(
        user_id=user_id, client_id=client_id, client_secret=client_secret
    )

    if not token_result.get("success"):
        log.info(f"!! Failed to get valid token: {token_result.get('error')}")

        return {"success": False, "error": token_result.get("error")}

    access_token = token_result.get("access_token", "")

    treatment_result = FullscriptAPI.create_treatment_plan(access_token, medications, patient_id)

    log.info(f"!! Fullscript create treatment plan: {treatment_result}")

    if treatment_result.get("success"):
        treatment_id = treatment_result.get("treatment_plan_id", [])
        log.info(f"!! Fullscript create treatment plan success: {treatment_id}")

        checkout_result = FullscriptAPI.create_treatment_checkout(access_token, treatment_id)

        if checkout_result.get("success"):
            checkout_url = checkout_result.get("checkout_url", "")
            log.info(f"!! Fullscript create treatment checkout success: {checkout_url}")

            return {"success": True, "checkout_url": checkout_url}
        else:
            log.info(
                f"!! Fullscript create treatment checkout failed: {checkout_result.get('error')}"
            )

            return {"success": False, "error": checkout_result.get("error")}

    else:
        log.info(f"!! Fullscript create treatment plan failed: {treatment_result.get('error')}")

        return {"success": False, "error": treatment_result.get("error")}


class CreateTreatmentPlanButton(ActionButton):
    """Button to create a Fullscript treatment plan from prescribe commands in the note."""

    BUTTON_TITLE = "Send supplements to patient"
    BUTTON_KEY = "CREATE_FULLSCRIPT_TREATMENT_PLAN"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_FOOTER

    def visible(self) -> bool:
        """Determine if the button should be visible based on secrets."""
        return self.secrets.get("FULLSCRIPT_API_ENABLED", "false").lower() == "true"

    def handle(self) -> list[Effect]:
        """Handle the button click to create a Fullscript treatment plan."""
        log.info("Button clicked!")
        log.info(self.context)
        log.info(self.target)

        note_id = (
            Note.objects.filter(dbid=self.context.get("note_id"))
            .values_list("id", flat=True)
            .first()
        )

        result = handle_treatment_plan(
            patient_id=self.target,
            note_id=note_id,
            user_id=self.context.get("user", {}).get("id"),
            secrets=self.secrets,
        )

        if result.get("success"):
            checkout_url = result.get("checkout_url", "")
            log.info(f"!! Fullscript treatment plan created successfully: {checkout_url}")
        else:
            log.info(f"!! Fullscript treatment plan creation failed: {result.get('error')}")

        return []


class LaunchFullscriptApplicationButton(ActionButton):
    """Button to launch the Fullscript application in a modal."""

    BUTTON_TITLE = "Open Fullscript Application"
    BUTTON_KEY = "OPEN_FULLSCRIPT_APPLICATION"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER

    def visible(self) -> bool:
        """Determine if the button should be visible."""
        note_id = self.context.get("note_id", None)

        allowed_note_types = (
            [t.strip() for t in self.secrets["FULLSCRIPT_NOTE_TYPES"].split(",")]
            if self.secrets["FULLSCRIPT_NOTE_TYPES"]
            else []
        )

        if allowed_note_types:
            # Verify that the note type is allowed
            note = Note.objects.filter(
                dbid=note_id, note_type_version__name__in=allowed_note_types
            ).exists()

            if not note:
                log.info(
                    f"Note type is not allowed for Fullscript application. Allowed types: {allowed_note_types}"
                )
                return False

        return True

    def handle(self) -> list[Effect]:
        """Handle the button click to launch the Fullscript application."""
        log.info("Button clicked!")
        log.info(self.context)
        log.info(self.target)

        patient_key = self.target
        note_id = self.context.get("note_id", None)
        params = self.context["params"] if self.context.get("params") else {}

        url = get_application_url(params, patient_key, note_id)

        return [
            LaunchModalEffect(
                url=url,
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
            ).apply()
        ]


class CreateTreatmentPlan(BaseHandler):
    """Protocol to add Fullscript supplement products to prescribe search results with clinical quantities."""

    RESPONDS_TO = EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED)

    def compute(self) -> list[Effect]:
        """Create a treatment plan in Fullscript based on the note update."""
        if self.secrets.get("FULLSCRIPT_API_ENABLED", "false").lower() != "true":
            log.info("!! Fullscript API is not enabled, skipping treatment plan creation")
            return []

        note_event_id = self.target  # Note state change event id
        patient_id = self.context.get("patient_id")
        state = self.context.get("state")
        note_id = self.context.get("note_id")

        note_event = NoteStateChangeEvent.objects.get(id=note_event_id)
        originator = note_event.originator
        user_id = originator.staff.id

        log.info(f"!! USER {user_id}")
        log.info(f"!! STATE {state}")

        if state != "LKD":
            log.info("!! Note state is not LKD, skipping Fullscript treatment plan creation")
            return []

        log.info(f"!! Note ID {note_id}")

        result = handle_treatment_plan(
            patient_id=patient_id, note_id=note_id, user_id=user_id, secrets=self.secrets
        )

        if result.get("success"):
            checkout_url = result.get("checkout_url", "")
            log.info(f"!! Fullscript treatment plan created successfully: {checkout_url}")
            return []
        else:
            log.info(f"!! Fullscript treatment plan creation failed: {result.get('error')}")
            return []

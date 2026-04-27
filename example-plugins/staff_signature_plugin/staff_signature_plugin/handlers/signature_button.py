from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.action_button import ActionButton


class StaffSignatureButton(ActionButton):
    """Chart header button that opens a modal showing the logged-in staff's signature."""

    BUTTON_TITLE = "My Signature"
    BUTTON_KEY = "staff_signature_button"
    BUTTON_LOCATION = ActionButton.ButtonLocation.CHART_PATIENT_HEADER
    PRIORITY = 1

    def handle(self) -> list[Effect]:
        """Open a modal that loads the signature view from the plugin API."""
        return [
            LaunchModalEffect(
                url="/plugin-io/api/staff_signature_plugin/signature",
                target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
                title="Staff Signature",
            ).apply()
        ]

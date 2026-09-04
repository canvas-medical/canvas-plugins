from canvas_sdk.effects import Effect
from canvas_sdk.effects.phone_dial_configuration import (
    PhoneDialClickHandling,
    PhoneDialConfiguration,
    PhoneDialSection,
)
from canvas_sdk.effects.redirect import RedirectEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

# Zoom's desktop client registers this scheme. The composed URL must also match an entry in
# the plugin's REDIRECT_ALLOWLIST_EXTERNAL secret or the redirect is blocked server-side.
#
# Built by concatenation rather than str.format: the sandbox blocks format and format_map on
# str, and it does so when the method is looked up at call time, so `canvas validate` loads
# the handler happily and the failure only appears on the first click.
ZOOM_DIAL_URL_PREFIX = "zoomus://zoom.us/call?number="


class ClickToDialConfiguration(BaseHandler):
    """Make every chart phone number clickable, and say who dials it.

    Three effects, because each group differs. A contact is plugin-driven and labelled, so the
    chart offers a "Dial number with Zoom" button. The patient's own numbers are plugin-driven
    but unlabelled, so the number itself is the link and the click is only recorded. An
    external care team number is left to the device's phone app.
    """

    RESPONDS_TO = EventType.Name(EventType.PHONE_DIAL__GET_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Return the sections whose phone numbers are clickable."""
        return [
            PhoneDialConfiguration(
                clickable_sections=[PhoneDialSection.CONTACT],
                click_handling=PhoneDialClickHandling.PLUGIN,
                dial_label="Zoom",
            ).apply(),
            PhoneDialConfiguration(
                clickable_sections=[PhoneDialSection.PATIENT],
                click_handling=PhoneDialClickHandling.PLUGIN,
            ).apply(),
            PhoneDialConfiguration(
                clickable_sections=[PhoneDialSection.EXTERNAL_CARE_TEAM],
                click_handling=PhoneDialClickHandling.DEVICE,
            ).apply(),
        ]


class PlaceCall(BaseHandler):
    """Dial through Zoom when a chart phone number is clicked.

    Every clickable number is dialed the same way, whatever section it came from. The
    configuration decides only the affordance: a labelled section offers a button naming
    Zoom, an unlabelled one makes the number itself the target.

    The event also fires for sections left to the device's phone app, which would then dial
    twice. A plugin that wants to dial only some sections reads ``source`` from the context
    and returns nothing for the rest.
    """

    RESPONDS_TO = EventType.Name(EventType.PHONE_NUMBER_CLICKED)

    def compute(self) -> list[Effect]:
        """Hand the clicked number to Zoom."""
        number = self.event.context["phone_number"]
        digits = "".join(character for character in number if character.isdigit())

        # A real integration might also create a task or notify a CRM here. Keep the number
        # out of anything it writes: a patient's phone number is PHI, and plugin logs are
        # shipped off the instance.
        return [
            RedirectEffect(
                url=f"{ZOOM_DIAL_URL_PREFIX}{digits}",
                # SAME_TAB hands the scheme to the OS and leaves the chart in place. A new tab
                # is unavailable here: the redirect arrives over a subscription rather than
                # inside the click, so opening one would be popup-blocked.
                target=RedirectEffect.TargetType.SAME_TAB,
            ).apply()
        ]

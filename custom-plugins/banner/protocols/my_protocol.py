from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol

from canvas_sdk.effects import AddBannerAlert, RemoveBannerAlert


# Inherit from BaseProtocol to properly get registered for events
class Protocol(BaseProtocol):
    """
    You should put a helpful description of this protocol's behavior here.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.CONDITION_CREATED)

    NARRATIVE_STRING = "I was inserted from my plugin's protocol."

    def compute(self):
        """
        This method gets called when an event of the type RESPONDS_TO is fired.
        """
        banner = AddBannerAlert(
            patient_key="c0d73e1abc284fdf9ebb23f21d1b5e27",
            key="first_banner",
            narrative="helloooo",
            placement=[AddBannerAlert.Placement.CHART],
            intent=AddBannerAlert.Intent.INFO,
            href="https://www.canvasmedical.com/",
        )
        remove = RemoveBannerAlert(patient_key="c0d73e1abc284fdf9ebb23f21d1b5e27", key="new_banner")

        return [banner.apply(), remove.apply()]

from canvas_sdk.effects import Effect
from canvas_sdk.effects.default_homepage import DefaultHomepageEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class Homepage(BaseHandler):
    """Handler for homepage configuration events."""

    RESPONDS_TO = EventType.Name(EventType.HOMEPAGE_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Set the default homepage."""
        user = self.event.target

        log.info(f"Setting default homepage for user {user.id}")

        return [
            DefaultHomepageEffect(
                application_url="/application/#application=YXZhaWxhYmlsaXR5X21hbmFnZXIuYXBwbGljYXRpb25zLm15X2FwcGxpY2F0aW9uOk15QXBwbGljYXRpb24%3D"
            ).apply()
        ]

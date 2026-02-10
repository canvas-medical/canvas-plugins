from canvas_sdk.effects import Effect
from canvas_sdk.effects.default_homepage import DefaultHomepageEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Application
from canvas_sdk.v1.data.staff import Staff
from logger import log


class Homepage(BaseHandler):
    """Handler for homepage configuration events."""

    RESPONDS_TO = EventType.Name(EventType.GET_HOMEPAGE_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Set the default homepage."""
        user_id = self.event.actor.id

        provider = Staff.objects.get(user_id=user_id)
        application = Application.objects.filter(name="custom_homepage").first()

        if provider.first_name == "Pedro":
            # should fail validation since application doesn't exist
            log.info("HOMEPAGE - SCHEDULE")
            return [DefaultHomepageEffect(application_identifier="no_app").apply()]

        if provider.first_name == "Larry" and application:
            log.info("HOMEPAGE - APPLICATION")
            return [DefaultHomepageEffect(application_identifier=application.identifier).apply()]

        log.info("HOMEPAGE - PAGE")
        return [DefaultHomepageEffect(page=DefaultHomepageEffect.Pages.PATIENTS).apply()]

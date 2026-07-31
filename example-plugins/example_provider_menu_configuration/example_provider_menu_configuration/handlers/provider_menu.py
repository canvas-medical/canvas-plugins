from canvas_sdk.effects import Effect
from canvas_sdk.effects.default_homepage import DefaultHomepageEffect
from canvas_sdk.effects.panel_configuration import PanelConfiguration
from canvas_sdk.effects.provider_menu_configuration import ProviderMenuConfiguration
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

Items = ProviderMenuConfiguration.Items
GlobalSection = PanelConfiguration.PanelGlobalSection


class HideScheduleMenuItem(BaseHandler):
    """Render every provider menu item except Schedule."""

    RESPONDS_TO = EventType.Name(EventType.GET_PROVIDER_MENU_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Return the allow-list of menu items to render.

        The effect replaces the default set, so every item that should stay
        visible has to be listed. Omitting Schedule is what hides it.
        """
        return [
            ProviderMenuConfiguration(
                items=[
                    Items.PATIENTS,
                    Items.REVENUE,
                    Items.POPULATIONS,
                    Items.CAMPAIGNS,
                    Items.DATA_INTEGRATION,
                    Items.QUESTIONNAIRE_BUILDER,
                    Items.SETTINGS,
                    Items.MULTI_FACTOR_AUTHENTICATION,
                    Items.CHANGELOG,
                    Items.HELP_CENTER,
                ]
            ).apply()
        ]


class HideAppointmentsPanelFilter(BaseHandler):
    """Drop the Appointments filter from the global panel's preset filters.

    This is a separate, already-released effect: `ProviderMenuConfiguration`
    governs the hamburger menu only, so the panel's Appointments filter has to be
    hidden through `PanelConfiguration`.
    """

    RESPONDS_TO = EventType.Name(EventType.PANEL_SECTIONS_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Return the global panel's sections, minus Appointments.

        The same event fires for both the global panel and a patient's panel, and
        only the global one has an Appointments section. A patient's panel is
        identified by the event carrying a target, so skip those and leave the
        patient panel alone.
        """
        if self.event.target.id:
            return []

        return [
            PanelConfiguration(
                sections=[
                    GlobalSection.CHANGE_REQUEST,
                    GlobalSection.IMAGING_REPORT,
                    GlobalSection.INPATIENT_STAY,
                    GlobalSection.LAB_REPORT,
                    GlobalSection.MESSAGE,
                    GlobalSection.OUTSTANDING_REFERRAL,
                    GlobalSection.PRESCRIPTION_ALERT,
                    GlobalSection.RECALL_APPOINTMENT,
                    GlobalSection.REFERRAL_REPORT,
                    GlobalSection.REFILL_REQUEST,
                    GlobalSection.TASK,
                    GlobalSection.UNCATEGORIZED_DOCUMENT,
                ],
                page=PanelConfiguration.Page.GLOBAL,
            ).apply()
        ]


class LandOnPatientsInsteadOfSchedule(BaseHandler):
    """Move the default landing page off the native schedule page.

    Hiding the Schedule menu item does not change where providers land after
    logging in — that still defaults to the schedule page. A plugin that hides
    the item should also claim the homepage, or providers arrive on a page they
    can no longer navigate back to.
    """

    RESPONDS_TO = EventType.Name(EventType.GET_HOMEPAGE_CONFIGURATION)

    def compute(self) -> list[Effect]:
        """Send providers to the patients page on login."""
        return [DefaultHomepageEffect(page=DefaultHomepageEffect.Pages.PATIENTS).apply()]

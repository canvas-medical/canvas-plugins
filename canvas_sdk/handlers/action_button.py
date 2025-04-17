import re
from abc import abstractmethod
from enum import StrEnum

from canvas_sdk.effects import Effect
from canvas_sdk.effects.show_button import ShowButtonEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler

SHOW_BUTTON_REGEX = re.compile(r"^SHOW_(.+?)_BUTTON$")


class ActionButton(BaseHandler):
    """Base class for action buttons."""

    RESPONDS_TO = [
        EventType.Name(EventType.SHOW_NOTE_HEADER_BUTTON),
        EventType.Name(EventType.SHOW_NOTE_FOOTER_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_SOCIAL_DETERMINANTS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_GOALS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_CONDITIONS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_MEDICATIONS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_ALLERGIES_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_CARE_TEAMS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_VITALS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_IMMUNIZATIONS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_SURGICAL_HISTORY_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_FAMILY_HISTORY_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_CODING_GAPS_SECTION_BUTTON),
        EventType.Name(EventType.ACTION_BUTTON_CLICKED),
    ]

    class ButtonLocation(StrEnum):
        NOTE_HEADER = "note_header"
        NOTE_FOOTER = "note_footer"
        CHART_SUMMARY_SOCIAL_DETERMINANTS_SECTION = "chart_summary_social_determinants_section"
        CHART_SUMMARY_GOALS_SECTION = "chart_summary_goals_section"
        CHART_SUMMARY_CONDITIONS_SECTION = "chart_summary_conditions_section"
        CHART_SUMMARY_MEDICATIONS_SECTION = "chart_summary_medications_section"
        CHART_SUMMARY_ALLERGIES_SECTION = "chart_summary_allergies_section"
        CHART_SUMMARY_CARE_TEAMS_SECTION = "chart_summary_care_teams_section"
        CHART_SUMMARY_VITALS_SECTION = "chart_summary_vitals_section"
        CHART_SUMMARY_IMMUNIZATIONS_SECTION = "chart_summary_immunizations_section"
        CHART_SUMMARY_SURGICAL_HISTORY_SECTION = "chart_summary_surgical_history_section"
        CHART_SUMMARY_FAMILY_HISTORY_SECTION = "chart_summary_family_history_section"
        CHART_SUMMARY_CODING_GAPS_SECTION = "chart_summary_coding_gaps_section"

    BUTTON_TITLE: str = ""
    BUTTON_KEY: str = ""
    BUTTON_LOCATION: ButtonLocation
    PRIORITY: int = 0

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Method to handle button click."""
        raise NotImplementedError("Implement to handle button click")

    def visible(self) -> bool:
        """Method to determine button visibility."""
        return True

    def compute(self) -> list[Effect]:
        """Method to compute the effects."""
        if not self.BUTTON_LOCATION:
            return []

        show_button_event_match = SHOW_BUTTON_REGEX.fullmatch(self.event.name)

        if show_button_event_match:
            location = show_button_event_match.group(1)
            if self.ButtonLocation[location] == self.BUTTON_LOCATION and self.visible():
                return [
                    ShowButtonEffect(
                        key=self.BUTTON_KEY, title=self.BUTTON_TITLE, priority=self.PRIORITY
                    ).apply()
                ]
        elif self.context["key"] == self.BUTTON_KEY:
            return self.handle()

        return []


__exports__ = (
    "SHOW_BUTTON_REGEX",
    "ActionButton",
)

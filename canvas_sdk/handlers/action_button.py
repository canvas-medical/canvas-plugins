from abc import abstractmethod
from enum import StrEnum

from canvas_sdk.effects import Effect
from canvas_sdk.effects.show_button import ShowButtonEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler


class ActionButton(BaseHandler):
    """Base class for action buttons."""

    RESPONDS_TO = [
        EventType.Name(EventType.SHOW_NOTE_HEADER_BUTTON),
        EventType.Name(EventType.SHOW_NOTE_FOOTER_BUTTON),
        EventType.Name(EventType.ACTION_BUTTON_CLICKED),
    ]

    class ButtonLocation(StrEnum):
        NOTE_HEADER = "note_header"
        NOTE_FOOTER = "note_footer"

    BUTTON_TITLE: str = ""
    BUTTON_KEY: str = ""
    BUTTON_LOCATION: ButtonLocation | None = None

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Method to handle button click."""
        raise NotImplementedError("Implement to handle button click")

    def visible(self) -> bool:
        """Method to determine button visibility."""
        return True

    def compute(self) -> list[Effect]:
        """Method to compute the effects."""
        if self.BUTTON_LOCATION is None:
            return []

        if self.event.type in (
            EventType.SHOW_NOTE_HEADER_BUTTON,
            EventType.SHOW_NOTE_FOOTER_BUTTON,
        ):
            if self.context["location"].lower() == self.BUTTON_LOCATION.value and self.visible():
                return [ShowButtonEffect(key=self.BUTTON_KEY, title=self.BUTTON_TITLE).apply()]
            else:
                return []
        elif (
            self.event.type == EventType.ACTION_BUTTON_CLICKED
            and self.context["key"] == self.BUTTON_KEY
        ):
            return self.handle()

        return []

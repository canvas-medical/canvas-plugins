from abc import abstractmethod
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class PatientChartSummaryCustomSectionHandler(BaseHandler):
    """Custom Chart Section Handler."""

    SECTION_KEY: str

    RESPONDS_TO = [
        EventType.Name(EventType.PATIENT_CHART_SUMMARY__GET_CUSTOM_SECTION),
    ]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "SECTION_KEY", None):
            raise ImproperlyConfigured(f"{cls.__name__!r} must define SECTION_KEY.")

    def accept_event(self) -> bool:
        """Accept an event if section matches."""
        return self.event.context.get("section") == self.SECTION_KEY

    def compute(self) -> list[Effect]:
        """Compute the effects for this handler."""
        return self.handle()

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Subclasses should implement this method."""
        raise NotImplementedError


__exports__ = ("PatientChartSummaryCustomSectionHandler",)

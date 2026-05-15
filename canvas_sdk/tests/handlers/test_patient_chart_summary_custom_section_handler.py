import json

import pytest
from django.core.exceptions import ImproperlyConfigured

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.patient_chart_summary_custom_section_handler import (
    PatientChartSummaryCustomSectionHandler,
)


class CustomChartSection(PatientChartSummaryCustomSectionHandler):
    """Concrete implementation for testing."""

    SECTION_KEY = "custom_section"

    def handle(self) -> list[Effect]:
        """Return an effect list."""
        return []


def make_event(section: str | None = None) -> Event:
    """Build a PATIENT_CHART_SUMMARY__GET_CUSTOM_SECTION event with optional section context."""
    context = json.dumps({"section": section}) if section is not None else ""
    return Event(
        EventRequest(
            type=EventType.PATIENT_CHART_SUMMARY__GET_CUSTOM_SECTION,
            context=context,
        )
    )


def test_missing_section_key_raises() -> None:
    """Subclasses without SECTION_KEY must raise ImproperlyConfigured at definition time."""
    with pytest.raises(ImproperlyConfigured, match="must define"):

        class NoSectionKey(PatientChartSummaryCustomSectionHandler):
            def handle(self) -> list[Effect]:
                return []


def test_empty_section_key_raises() -> None:
    """Subclasses with an empty SECTION_KEY must raise ImproperlyConfigured."""
    with pytest.raises(ImproperlyConfigured, match="must define"):

        class EmptySectionKey(PatientChartSummaryCustomSectionHandler):
            SECTION_KEY = ""

            def handle(self) -> list[Effect]:
                return []


def test_valid_section_key_does_not_raise() -> None:
    """Subclasses with a non-empty SECTION_KEY must not raise."""

    class ValidSectionSection(PatientChartSummaryCustomSectionHandler):
        SECTION_KEY = "some_section"

        def handle(self) -> list[Effect]:
            return []


def test_responds_to_contains_get_custom_section_event() -> None:
    """RESPONDS_TO must include PATIENT_CHART_SUMMARY__GET_CUSTOM_SECTION."""
    assert (
        EventType.Name(EventType.PATIENT_CHART_SUMMARY__GET_CUSTOM_SECTION)
        in PatientChartSummaryCustomSectionHandler.RESPONDS_TO
    )


def test_accept_event_returns_true_for_matching_section() -> None:
    """accept_event must return True when the event section matches SECTION_KEY."""
    handler = CustomChartSection(make_event("custom_section"))
    assert handler.accept_event() is True


def test_accept_event_returns_false_for_different_section() -> None:
    """accept_event must return False when the event section does not match SECTION_KEY."""
    handler = CustomChartSection(make_event("other_section"))
    assert handler.accept_event() is False


def test_accept_event_returns_false_when_section_missing_from_context() -> None:
    """accept_event must return False when the event context has no section key."""
    handler = CustomChartSection(make_event())
    assert handler.accept_event() is False

"""Unit tests for the Imaging Template Explorer plugin."""

import pytest

from imaging_template_explorer.protocols.imaging_template_api import (
    ImagingTemplateAPI,
    ImagingTemplateProtocolCard,
)


class TestImagingTemplateAPI:
    """Tests for the ImagingTemplateAPI Simple API handler."""

    def test_handler_has_correct_path(self) -> None:
        """Ensure the handler is registered at the correct path."""
        assert ImagingTemplateAPI.PATH == "/imaging-templates/<patient_id>"

    def test_handler_has_get_method(self) -> None:
        """Ensure the handler has a get method."""
        assert hasattr(ImagingTemplateAPI, "get")
        assert callable(getattr(ImagingTemplateAPI, "get"))

    def test_handler_inherits_from_simple_api_route(self) -> None:
        """Ensure the handler inherits from SimpleAPIRoute."""
        from canvas_sdk.handlers.simple_api import SimpleAPIRoute

        assert issubclass(ImagingTemplateAPI, SimpleAPIRoute)


class TestImagingTemplateProtocolCard:
    """Tests for the ImagingTemplateProtocolCard protocol handler."""

    def test_responds_to_correct_event(self) -> None:
        """Ensure the protocol responds to the correct event type."""
        from canvas_sdk.events import EventType

        expected = EventType.Name(EventType.PATIENT_CHART_SUMMARY__SECTION_CONFIGURATION)
        assert ImagingTemplateProtocolCard.RESPONDS_TO == expected

    def test_handler_has_compute_method(self) -> None:
        """Ensure the handler has a compute method."""
        assert hasattr(ImagingTemplateProtocolCard, "compute")
        assert callable(getattr(ImagingTemplateProtocolCard, "compute"))

    def test_handler_inherits_from_base_protocol(self) -> None:
        """Ensure the handler inherits from BaseProtocol."""
        from canvas_sdk.protocols import BaseProtocol

        assert issubclass(ImagingTemplateProtocolCard, BaseProtocol)

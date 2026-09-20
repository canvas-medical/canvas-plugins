from lab_template_explorer.protocols.lab_template_api import (
    LabTemplateAPI,
    LabTemplateProtocolCard,
)


class TestLabTemplateAPI:
    """Tests for the LabTemplateAPI Simple API handler."""

    def test_handler_has_correct_path(self) -> None:
        """Ensure the handler is registered at the correct path."""
        assert LabTemplateAPI.PATH == "/lab-templates/<patient_id>"

    def test_handler_has_get_method(self) -> None:
        """Ensure the handler has a get method."""
        assert hasattr(LabTemplateAPI, "get")
        assert callable(LabTemplateAPI.get)

    def test_handler_inherits_from_simple_api_route(self) -> None:
        """Ensure the handler inherits from SimpleAPIRoute."""
        from canvas_sdk.handlers.simple_api import SimpleAPIRoute

        assert issubclass(LabTemplateAPI, SimpleAPIRoute)


class TestLabTemplateProtocolCard:
    """Tests for the LabTemplateProtocolCard protocol handler."""

    def test_responds_to_correct_event(self) -> None:
        """Ensure the protocol responds to the correct event type."""
        from canvas_sdk.events import EventType

        expected = EventType.Name(EventType.PATIENT_CHART_SUMMARY__SECTION_CONFIGURATION)
        assert expected == LabTemplateProtocolCard.RESPONDS_TO

    def test_handler_has_compute_method(self) -> None:
        """Ensure the handler has a compute method."""
        assert hasattr(LabTemplateProtocolCard, "compute")
        assert callable(LabTemplateProtocolCard.compute)

    def test_handler_inherits_from_base_protocol(self) -> None:
        """Ensure the handler inherits from BaseProtocol."""
        from canvas_sdk.protocols import BaseProtocol

        assert issubclass(LabTemplateProtocolCard, BaseProtocol)

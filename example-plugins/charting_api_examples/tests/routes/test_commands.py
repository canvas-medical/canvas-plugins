"""Tests for charting_api_examples.routes.commands module."""

from unittest.mock import MagicMock

from charting_api_examples.routes.commands import CommandAPI


class TestCommandAPI:
    """Tests for CommandAPI class."""

    def test_prefix_configuration(self):
        """Test that the API prefix is correctly configured."""
        assert CommandAPI.PREFIX == "/notes"

    def test_api_inherits_from_expected_classes(self):
        """Test that CommandAPI inherits from the correct base classes."""
        from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI

        assert issubclass(CommandAPI, APIKeyAuthMixin)
        assert issubclass(CommandAPI, SimpleAPI)

    def test_api_instance_creation(self):
        """Test that CommandAPI can be instantiated."""
        mock_event = MagicMock()
        api = CommandAPI(event=mock_event)
        assert api is not None
        assert hasattr(api, "add_diagnose_command")
        assert hasattr(api, "add_precharting_commands")

"""Tests for example_patient_portal_page.handlers.my_web_app module."""

from unittest.mock import MagicMock

from example_patient_portal_page.handlers.my_web_app import MyWebApp


class TestMyWebApp:
    """Tests for MyWebApp class."""

    def test_prefix_configuration(self):
        """Test that the API prefix is correctly configured."""
        assert MyWebApp.PREFIX == "/app"

    def test_inherits_from_simple_api(self):
        """Test that MyWebApp inherits from SimpleAPI."""
        from canvas_sdk.handlers.simple_api import SimpleAPI

        assert issubclass(MyWebApp, SimpleAPI)

    def test_authenticate_with_logged_in_user(self):
        """Test that authenticate returns True when user is logged in."""
        mock_event = MagicMock()
        app = MyWebApp(event=mock_event)

        mock_credentials = MagicMock()
        mock_credentials.logged_in_user = MagicMock()

        assert app.authenticate(mock_credentials) is True

    def test_authenticate_with_no_logged_in_user(self):
        """Test that authenticate returns False when user is not logged in."""
        mock_event = MagicMock()
        app = MyWebApp(event=mock_event)

        mock_credentials = MagicMock()
        mock_credentials.logged_in_user = None

        assert app.authenticate(mock_credentials) is False

    def test_api_instance_creation(self):
        """Test that MyWebApp can be instantiated."""
        mock_event = MagicMock()
        app = MyWebApp(event=mock_event)
        assert app is not None
        assert hasattr(app, "index")
        assert hasattr(app, "get_main_js")
        assert hasattr(app, "get_css")

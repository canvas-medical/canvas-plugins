"""Tests for example_chart_app.applications.my_application module."""

from unittest.mock import MagicMock, patch

from example_chart_app.applications.my_application import MyChartApplication, MyApi


class TestMyChartApplication:
    """Tests for MyChartApplication class."""

    def test_inherits_from_application(self):
        """Test that MyChartApplication inherits from Application."""
        from canvas_sdk.handlers.application import Application

        assert issubclass(MyChartApplication, Application)

    def test_on_open_returns_effect(self):
        """Test that on_open returns a LaunchModalEffect."""
        patient_id = "patient-123"
        mock_event = MagicMock()
        mock_event.context = {"patient": {"id": patient_id}}
        app = MyChartApplication(event=mock_event)

        with patch(
            "example_chart_app.applications.my_application.LaunchModalEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_applied = MagicMock()
            mock_effect_instance.apply.return_value = mock_applied
            mock_effect.return_value = mock_effect_instance

            result = app.on_open()

            # Verify LaunchModalEffect was created with correct URL
            mock_effect.assert_called_once()
            call_kwargs = mock_effect.call_args[1]
            assert f"patient={patient_id}" in call_kwargs["url"]
            assert call_kwargs["target"] == mock_effect.TargetType.RIGHT_CHART_PANE

            # Verify apply was called
            mock_effect_instance.apply.assert_called_once()
            assert result == mock_applied


class TestMyApi:
    """Tests for MyApi class."""

    def test_inherits_from_expected_classes(self):
        """Test that MyApi inherits from the correct base classes."""
        from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin

        assert issubclass(MyApi, StaffSessionAuthMixin)
        assert issubclass(MyApi, SimpleAPI)

    def test_api_instance_creation(self):
        """Test that MyApi can be instantiated."""
        mock_event = MagicMock()
        api = MyApi(event=mock_event)
        assert api is not None
        assert hasattr(api, "custom_ui")
        assert hasattr(api, "add_task")

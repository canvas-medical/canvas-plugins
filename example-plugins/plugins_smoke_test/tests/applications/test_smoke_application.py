"""Tests for plugins_smoke_test.applications.my_application module."""

from unittest.mock import MagicMock, patch

from plugins_smoke_test.applications.my_application import MyGlobalApplication, SmokeTestApi


class TestMyGlobalApplication:
    """Tests for MyGlobalApplication class."""

    def test_inherits_from_application(self):
        """Test that MyGlobalApplication inherits from Application."""
        from canvas_sdk.handlers.application import Application

        assert issubclass(MyGlobalApplication, Application)

    def test_on_open_returns_launch_modal_effect(self):
        """Test that on_open returns a LaunchModalEffect with correct configuration."""
        mock_event = MagicMock()
        app = MyGlobalApplication(event=mock_event)

        with patch(
            "plugins_smoke_test.applications.my_application.LaunchModalEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_applied = MagicMock()
            mock_effect_instance.apply.return_value = mock_applied
            mock_effect.return_value = mock_effect_instance

            result = app.on_open()

            # Verify LaunchModalEffect was created with correct parameters
            mock_effect.assert_called_once_with(
                url="/plugin-io/api/plugins_smoke_test/global",
                target=mock_effect.TargetType.DEFAULT_MODAL,
            )
            mock_effect_instance.apply.assert_called_once()
            assert result == mock_applied


class TestSmokeTestApi:
    """Tests for SmokeTestApi class."""

    def test_inherits_from_expected_classes(self):
        """Test that SmokeTestApi inherits from the correct base classes."""
        from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin

        assert issubclass(SmokeTestApi, StaffSessionAuthMixin)
        assert issubclass(SmokeTestApi, SimpleAPI)

    def test_api_instance_creation(self):
        """Test that SmokeTestApi can be instantiated."""
        mock_event = MagicMock()
        api = SmokeTestApi(event=mock_event)
        assert api is not None
        assert hasattr(api, "smoke_test_ui")
        assert hasattr(api, "add_task")

"""Tests for example_provider_page.applications.my_application module."""

from unittest.mock import MagicMock, patch

from example_provider_page.applications.my_application import MyApplication


class TestMyApplication:
    """Tests for MyApplication class."""

    def test_inherits_from_application(self):
        """Test that MyApplication inherits from Application."""
        from canvas_sdk.handlers.application import Application

        assert issubclass(MyApplication, Application)

    def test_on_open_returns_launch_modal_effect(self):
        """Test that on_open returns a LaunchModalEffect with correct configuration."""
        mock_event = MagicMock()
        app = MyApplication(event=mock_event)

        with patch(
            "example_provider_page.applications.my_application.LaunchModalEffect"
        ) as mock_effect:
            mock_effect_instance = MagicMock()
            mock_applied = MagicMock()
            mock_effect_instance.apply.return_value = mock_applied
            mock_effect.return_value = mock_effect_instance

            result = app.on_open()

            # Verify LaunchModalEffect was created with correct parameters
            mock_effect.assert_called_once_with(
                url="/plugin-io/api/example_provider_page/app/provider-application",
                target=mock_effect.TargetType.PAGE,
            )
            mock_effect_instance.apply.assert_called_once()
            assert result == mock_applied

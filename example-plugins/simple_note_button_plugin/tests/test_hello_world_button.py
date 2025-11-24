from unittest.mock import MagicMock, patch

from simple_note_button_plugin.handlers.hello_world_button import HelloWorldButton


def test_hello_world_button_handle() -> None:
    """Test that the HelloWorldButton creates and applies a LaunchModalEffect."""
    # Create a HelloWorldButton instance with a mocked event
    button = HelloWorldButton(event=MagicMock())

    # Mock the LaunchModalEffect to verify it's created correctly
    with patch(
        "simple_note_button_plugin.handlers.hello_world_button.LaunchModalEffect"
    ) as mock_effect_class:
        mock_effect_instance = MagicMock()
        mock_applied_effect = MagicMock()
        mock_effect_instance.apply.return_value = mock_applied_effect
        mock_effect_class.return_value = mock_effect_instance

        # Call the handle method
        result = button.handle()

        # Verify LaunchModalEffect was created with correct parameters
        mock_effect_class.assert_called_once_with(
            content="<h1>Hello World!</h1><p>This is a simple Canvas plugin UI.</p>",
            target=mock_effect_class.TargetType.RIGHT_CHART_PANE,
            title="Hello World",
        )

        # Verify apply() was called
        mock_effect_instance.apply.assert_called_once()

        # Verify the result contains the applied effect
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == mock_applied_effect


def test_hello_world_button_configuration() -> None:
    """Test that the HelloWorldButton has the correct configuration."""
    assert HelloWorldButton.BUTTON_TITLE == "Hello World"
    assert HelloWorldButton.BUTTON_KEY == "hello_world_button"
    assert HelloWorldButton.BUTTON_LOCATION == HelloWorldButton.ButtonLocation.NOTE_HEADER
    assert HelloWorldButton.PRIORITY == 1

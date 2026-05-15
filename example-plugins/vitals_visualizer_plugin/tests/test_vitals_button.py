from unittest.mock import MagicMock, patch

from pytest import MonkeyPatch
from vitals_visualizer_plugin.handlers.vitals_button import VitalsVisualizerButton


def test_vitals_visualizer_button_configuration() -> None:
    """Test that the VitalsVisualizerButton has the correct configuration."""
    assert VitalsVisualizerButton.BUTTON_TITLE == "Visualize"
    assert VitalsVisualizerButton.BUTTON_KEY == "vitals_visualizer_button"
    assert (
        VitalsVisualizerButton.BUTTON_LOCATION
        == VitalsVisualizerButton.ButtonLocation.CHART_SUMMARY_VITALS_SECTION
    )
    assert VitalsVisualizerButton.PRIORITY == 1


def test_vitals_visualizer_button_handle(monkeypatch: MonkeyPatch) -> None:
    """Test that the button creates a LaunchModalEffect with correct URL and patient ID."""
    # Create button instance with mocked event
    button = VitalsVisualizerButton(event=MagicMock())

    # Mock the target (patient_id)
    test_patient_id = "test-patient-123"
    monkeypatch.setattr(type(button), "target", property(lambda self: test_patient_id))

    # Mock LaunchModalEffect
    with patch(
        "vitals_visualizer_plugin.handlers.vitals_button.LaunchModalEffect"
    ) as mock_effect_class:
        mock_effect_instance = MagicMock()
        mock_applied_effect = MagicMock()
        mock_effect_instance.apply.return_value = mock_applied_effect
        mock_effect_class.return_value = mock_effect_instance

        # Call the handle method
        result = button.handle()

        # Verify LaunchModalEffect was created with correct parameters
        expected_url = (
            f"/plugin-io/api/vitals_visualizer_plugin/visualize?patient_id={test_patient_id}"
        )
        mock_effect_class.assert_called_once_with(
            url=expected_url,
            target=mock_effect_class.TargetType.RIGHT_CHART_PANE_LARGE,
            title="Vitals Visualization",
        )

        # Verify apply() was called
        mock_effect_instance.apply.assert_called_once()

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == mock_applied_effect

from unittest.mock import MagicMock, patch

from lab_results_modal.handlers.lab_results_button import (
    LabResultsButton,
    _build_section,
)


def test_lab_results_button_configuration() -> None:
    """The button is configured for the patient chart header."""
    assert LabResultsButton.BUTTON_TITLE == "Lab Results"
    assert LabResultsButton.BUTTON_KEY == "lab_results_modal_button"
    assert LabResultsButton.BUTTON_LOCATION == LabResultsButton.ButtonLocation.CHART_PATIENT_HEADER


def test_handle_renders_template_and_launches_modal() -> None:
    """handle() queries reports for the chart's patient and renders them via the template."""
    event = MagicMock()
    event.target.id = "pt_123"
    button = LabResultsButton(event=event)

    fake_reports = [MagicMock()]

    with (
        patch("lab_results_modal.handlers.lab_results_button.LabReport.objects") as mock_objects,
        patch(
            "lab_results_modal.handlers.lab_results_button.LaunchModalEffect"
        ) as mock_effect_class,
        patch(
            "lab_results_modal.handlers.lab_results_button.render_to_string",
            return_value="<html></html>",
        ) as mock_render,
        patch(
            "lab_results_modal.handlers.lab_results_button._build_report_context",
            return_value={"stub": True},
        ),
    ):
        mock_objects.filter.return_value.order_by.return_value.with_result_tests_and_values.return_value = fake_reports
        mock_effect_instance = MagicMock()
        mock_effect_instance.apply.return_value = "applied"
        mock_effect_class.return_value = mock_effect_instance

        result = button.handle()

        mock_objects.filter.assert_called_once_with(
            patient__id="pt_123", junked=False, for_test_only=False
        )
        mock_render.assert_called_once_with(
            "templates/lab_results.html", {"reports": [{"stub": True}]}
        )
        mock_effect_class.assert_called_once_with(
            content="<html></html>",
            target=mock_effect_class.TargetType.DEFAULT_MODAL,
            title="Lab Results",
        )
        assert result == ["applied"]


def test_build_section_hides_ref_range_when_all_blank() -> None:
    """show_ref_range is False when no value carries a reference range."""
    values = [MagicMock(reference_range=""), MagicMock(reference_range="   ")]
    section = _build_section("Glucose", values)
    assert section == {"heading": "Glucose", "values": values, "show_ref_range": False}


def test_build_section_shows_ref_range_when_any_present() -> None:
    """show_ref_range is True when at least one value carries a reference range."""
    values = [MagicMock(reference_range=""), MagicMock(reference_range="70-99")]
    section = _build_section("Glucose", values)
    assert section["show_ref_range"] is True

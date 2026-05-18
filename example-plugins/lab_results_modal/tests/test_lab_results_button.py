from datetime import date
from unittest.mock import MagicMock, patch

from lab_results_modal.handlers.lab_results_button import (
    LabResultsButton,
    _build_report_context,
    _build_section,
)


def _make_value(*, test_id: str | None = None, reference_range: str = "") -> MagicMock:
    value = MagicMock()
    value.test_id = test_id
    value.reference_range = reference_range
    return value


def _make_test(*, ontology_test_name: str = "Glucose", values: list | None = None) -> MagicMock:
    test = MagicMock()
    test.ontology_test_name = ontology_test_name
    test.values.all.return_value = list(values or [])
    return test


def _make_report(
    *,
    result_tests: list | None = None,
    values: list | None = None,
    custom_document_name: str = "Doc",
    original_date: date | None = None,
) -> MagicMock:
    report = MagicMock()
    report.result_tests = list(result_tests or [])
    report.values.all.return_value = list(values or [])
    report.custom_document_name = custom_document_name
    report.original_date = original_date
    return report


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


def test_build_report_context_groups_result_tests_into_sections() -> None:
    """Each result test with values becomes a section labeled by ontology_test_name."""
    value = _make_value(test_id="t1")
    test = _make_test(ontology_test_name="Glucose", values=[value])
    report = _make_report(
        result_tests=[test],
        values=[value],
        custom_document_name="Annual Panel",
        original_date=date(2026, 5, 1),
    )

    context = _build_report_context(report)

    assert context["title"] == "Annual Panel"
    assert context["date"] == "2026-05-01"
    assert len(context["sections"]) == 1
    assert context["sections"][0]["heading"] == "Glucose"
    assert context["sections"][0]["values"] == [value]


def test_build_report_context_skips_tests_with_no_values() -> None:
    """A result test with zero values does not produce a section."""
    test = _make_test(values=[])
    report = _make_report(result_tests=[test])

    context = _build_report_context(report)

    assert context["sections"] == []


def test_build_report_context_falls_back_to_lab_test_heading() -> None:
    """When ontology_test_name is empty, the section heading falls back to 'Lab Test'."""
    value = _make_value(test_id="t1")
    test = _make_test(ontology_test_name="", values=[value])
    report = _make_report(result_tests=[test], values=[value])

    context = _build_report_context(report)

    assert context["sections"][0]["heading"] == "Lab Test"


def test_build_report_context_orphan_only_report_uses_empty_heading() -> None:
    """When the report has only orphan values, the orphan section heading is blank."""
    orphan = _make_value(test_id=None)
    report = _make_report(result_tests=[], values=[orphan])

    context = _build_report_context(report)

    assert len(context["sections"]) == 1
    assert context["sections"][0]["heading"] == ""
    assert context["sections"][0]["values"] == [orphan]


def test_build_report_context_orphans_alongside_tests_get_other_values_heading() -> None:
    """Orphan values are labeled 'Other values' when test sections are also present."""
    grouped = _make_value(test_id="t1")
    orphan = _make_value(test_id=None)
    test = _make_test(values=[grouped])
    report = _make_report(result_tests=[test], values=[grouped, orphan])

    context = _build_report_context(report)

    assert len(context["sections"]) == 2
    assert context["sections"][1]["heading"] == "Other values"
    assert context["sections"][1]["values"] == [orphan]


def test_build_report_context_falls_back_to_default_title() -> None:
    """When custom_document_name is empty, the title falls back to 'Lab Report'."""
    report = _make_report(custom_document_name="")

    context = _build_report_context(report)

    assert context["title"] == "Lab Report"


def test_build_report_context_uses_em_dash_when_no_original_date() -> None:
    """When original_date is None, the date string is the em-dash placeholder."""
    report = _make_report(original_date=None)

    context = _build_report_context(report)

    assert context["date"] == "—"

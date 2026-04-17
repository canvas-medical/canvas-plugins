from django.db.models import Prefetch

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.lab import LabReport, LabTest


class LabResultsButton(ActionButton):
    """Patient chart header button that opens a modal of the patient's lab results."""

    BUTTON_TITLE = "Lab Results"
    BUTTON_KEY = "lab_results_modal_button"
    BUTTON_LOCATION = ActionButton.ButtonLocation.CHART_PATIENT_HEADER
    PRIORITY = 1

    def handle(self) -> list[Effect]:
        """Render the patient's lab reports as HTML and launch a modal."""
        patient_id = self.event.target.id
        reports = (
            LabReport.objects.filter(patient__id=patient_id, junked=False, for_test_only=False)
            .order_by("-original_date")
            .prefetch_related(
                Prefetch(
                    "tests",
                    queryset=LabTest.objects.filter(order__isnull=True).prefetch_related("values"),
                ),
                "values",
            )
        )

        context = {"reports": [_build_report_context(r) for r in reports]}

        return [
            LaunchModalEffect(
                content=render_to_string("templates/lab_results.html", context),
                target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
                title="Lab Results",
            ).apply()
        ]


def _build_report_context(report: LabReport) -> dict:
    """Build the template context for a single LabReport."""
    sections = []
    for test in report.tests.all():
        values = list(test.values.all())
        if values:
            sections.append(_build_section(test.ontology_test_name or "Lab Test", values))

    # Orphan values: LabValues with no test FK. Happens for some data-integration
    # reports and for FHIR-API reports with `values_without_tests`.
    orphan_values = [v for v in report.values.all() if v.test_id is None]
    if orphan_values:
        # Only label the orphan section when it sits alongside test-grouped values;
        # otherwise the heading just looks redundant on reports with no tests at all.
        heading = "Other values" if sections else ""
        sections.append(_build_section(heading, orphan_values))

    return {
        "title": report.custom_document_name or "Lab Report",
        "date": report.original_date.strftime("%Y-%m-%d") if report.original_date else "—",
        "sections": sections,
    }


def _build_section(heading: str, values: list) -> dict:
    """Build a section context, hiding the reference-range column when every value is blank."""
    return {
        "heading": heading,
        "values": values,
        "show_ref_range": True,
    }

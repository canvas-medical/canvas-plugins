"""find_lab_results: what the lab reported for each value, including its normal range."""

from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    LabReportFactory,
    LabValueFactory,
    PatientFactory,
)


def _results(patient: Any) -> list[dict[str, Any]]:
    return standard_tools.execute("find_lab_results", {}, ctx={"patient_id": patient.id})


@pytest.mark.django_db
def test_each_result_carries_the_range_the_lab_reported() -> None:
    """A flag says a value is out of range; the range says what normal is."""
    patient = PatientFactory.create()
    report = LabReportFactory.create(patient=patient)
    LabValueFactory.create(
        report=report, value="7.4", units="%", abnormal_flag="H", reference_range="4.0-5.6"
    )

    (result,) = _results(patient)

    assert (result["value"], result["abnormal_flag"], result["reference_range"]) == (
        "7.4",
        "H",
        "4.0-5.6",
    )


@pytest.mark.django_db
def test_a_result_without_a_range_says_so() -> None:
    """Many labs send no range; the row carries null rather than an empty string."""
    patient = PatientFactory.create()
    LabValueFactory.create(report=LabReportFactory.create(patient=patient), reference_range="")

    (result,) = _results(patient)

    assert result["reference_range"] is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "removed",
    [{"deleted": True}, {"entered_in_error": True}, {"junked": True}],
    ids=["deleted", "entered in error", "junked"],
)
def test_a_report_taken_out_of_the_chart_returns_no_values(removed: dict[str, Any]) -> None:
    """A report deleted, entered in error, or junked is not a chart fact the model can cite."""
    patient = PatientFactory.create()
    LabValueFactory.create(report=LabReportFactory.create(patient=patient), value="kept")
    fields = dict(removed)
    if fields.pop("entered_in_error", False):
        fields["entered_in_error"] = CanvasUserFactory.create()
    LabValueFactory.create(report=LabReportFactory.create(patient=patient, **fields), value="gone")

    assert [result["value"] for result in _results(patient)] == ["kept"]

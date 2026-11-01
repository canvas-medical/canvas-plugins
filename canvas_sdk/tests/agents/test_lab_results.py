"""find_lab_results: what the lab reported for each value, including its normal range."""

from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import LabReportFactory, LabValueFactory, PatientFactory


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

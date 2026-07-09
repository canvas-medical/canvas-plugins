"""Attach lab tests/values to an existing lab report.

The effect itself is private — plugin authors use the fluent
``LabReport(report_id=...).attach_results([...])`` method
(:mod:`canvas_sdk.effects.lab_report.base`). Attaching is additive: it
appends tests/values to the report without removing existing ones.

A ``LabTest`` mirrors home-app's result-test row: it carries the
order/compendium code (``ontology_test_code``/``ontology_test_name`` — *not*
LOINC) and groups one or more ``LabValue``s. LOINC is supplied separately via
``codings`` on both the test and each value (reusing the ``Observation``
effect's :class:`CodingData`); the interpreter persists codings whose
``system`` is LOINC into ``OntologyLabTestLoincCode`` /
``OntologyLabTestValueLoincCode``.
"""

from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.effects.observation.base import CodingData


class ObservationStatus(StrEnum):
    """FHIR observation status for a lab value."""

    AMENDED = "amended"
    CANCELLED = "cancelled"
    CORRECTED = "corrected"
    ENTERED_IN_ERROR = "entered-in-error"
    FINAL = "final"
    PRELIMINARY = "preliminary"
    REGISTERED = "registered"
    UNKNOWN = "unknown"


class LabValue(BaseModel):
    """A single result value on a lab test.

    ``codings`` carry the value's LOINC coding(s), persisted server-side as
    ``OntologyLabTestValueLoincCode`` (only codings whose ``system`` is LOINC).
    """

    value: str
    units: str = ""
    reference_range: str = ""
    abnormal_flag: str = ""
    observation_status: ObservationStatus = ObservationStatus.FINAL
    comment: str = ""
    codings: list[CodingData] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the value into the proto payload dict."""
        return {
            "value": self.value,
            "units": self.units,
            "reference_range": self.reference_range,
            "abnormal_flag": self.abnormal_flag,
            "observation_status": self.observation_status.value,
            "comment": self.comment,
            "codings": (
                [coding.to_dict() for coding in self.codings] if self.codings is not None else None
            ),
        }


class LabTest(BaseModel):
    """A lab test grouping its result values.

    ``ontology_test_code``/``ontology_test_name`` are the order/compendium code
    and name (these live on ``LabTest`` in home-app and are *not* LOINC).
    ``codings`` carry the test's LOINC coding(s), persisted as
    ``OntologyLabTestLoincCode``.
    """

    ontology_test_code: str = ""
    ontology_test_name: str = ""
    codings: list[CodingData] | None = None
    values: list[LabValue] = Field(min_length=1)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the test (and its values) into the proto payload dict."""
        return {
            "ontology_test_code": self.ontology_test_code,
            "ontology_test_name": self.ontology_test_name,
            "codings": (
                [coding.to_dict() for coding in self.codings] if self.codings is not None else None
            ),
            "values": [value.to_dict() for value in self.values],
        }


class _LabReportAttachResults(_BaseEffect):
    """Attach lab tests/values to an existing report, identified by handle.

    Private — constructed by ``LabReport.attach_results``. Exactly one of
    ``report_id`` (Canvas externally-exposable id) or ``external_id`` (the
    plugin's handle) must be supplied.
    """

    class Meta:
        effect_type = EffectType.ATTACH_LAB_REPORT_RESULTS

    report_id: UUID | None = Field(default=None, strict=False)
    external_id: Annotated[str, Field(max_length=40)] = ""
    lab_tests: list[LabTest] = Field(min_length=1)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Require exactly one handle (report_id or external_id) on apply."""
        errors = super()._get_error_details(method)

        if method == "apply":
            handles = [handle for handle in (self.report_id, self.external_id) if handle]
            if len(handles) != 1:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Exactly one of report_id or external_id is required.",
                        handles,
                    )
                )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the effect's fields into the proto payload dict."""
        return {
            "report_id": str(self.report_id) if self.report_id else "",
            "external_id": self.external_id,
            "lab_tests": [test.to_dict() for test in self.lab_tests],
        }


__exports__ = ("LabTest", "LabValue", "ObservationStatus")

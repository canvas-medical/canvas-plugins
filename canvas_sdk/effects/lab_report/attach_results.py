"""Attach lab tests/values to an existing lab report.

The effect itself is private — plugin authors use the fluent
``LabReport(report_id=...).attach_results([...])`` method
(:mod:`canvas_sdk.effects.lab_report.base`). Attaching is additive: it
appends tests/values to the report without removing existing ones.
"""

from enum import StrEnum
from typing import Annotated, Any, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from canvas_sdk.effects.base import EffectType, _BaseEffect


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
    """A single lab value (and its implied test) to attach to a report."""

    ontology_test_code: str
    ontology_test_name: str = ""
    value: str
    units: str = ""
    reference_range: str = ""
    abnormal_flag: str = ""
    observation_status: ObservationStatus = ObservationStatus.FINAL
    comment: str = ""

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the value into the proto payload dict."""
        return self.model_dump(mode="json")


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
    lab_values: list[LabValue] = Field(min_length=1)

    @model_validator(mode="after")
    def _exactly_one_handle(self) -> Self:
        """Require exactly one of report_id / external_id."""
        handles = [handle for handle in (self.report_id, self.external_id) if handle]
        if len(handles) != 1:
            raise ValueError("Exactly one of report_id or external_id is required.")
        return self

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the effect's fields into the proto payload dict."""
        return {
            "report_id": str(self.report_id) if self.report_id else "",
            "external_id": self.external_id,
            "lab_values": [value.values for value in self.lab_values],
        }


__exports__ = ("LabValue", "ObservationStatus")

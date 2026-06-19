"""``LabReportAttachResults`` effect: attach tests/values to a report.

Additive — appends lab tests/values to an existing report (the async-OCR
case where the report is created first and values arrive later). Mirrors
the nested-children shape of the Health Gorilla lab ingest effect.
"""

from typing import Any

from pydantic import BaseModel
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class LabValue(BaseModel):
    """A single lab value (and its implied test) to attach to a report."""

    ontology_test_code: str
    ontology_test_name: str = ""
    value: str
    units: str = ""
    reference_range: str = ""
    abnormal_flag: str = ""
    observation_status: str = "final"
    comment: str = ""

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the value into the proto payload dict."""
        return self.model_dump()


class LabReportAttachResults(_BaseEffect):
    """Attach lab tests/values to an existing report, identified by handle.

    Exactly one of ``report_id`` (Canvas externally-exposable id) or
    ``external_id`` (the plugin's handle) must be supplied.
    """

    class Meta:
        effect_type = EffectType.ATTACH_LAB_REPORT_RESULTS

    report_id: str = ""
    external_id: str = ""
    lab_values: list[LabValue]

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the effect's fields into the proto payload dict."""
        return {
            "report_id": self.report_id,
            "external_id": self.external_id,
            "lab_values": [value.values for value in self.lab_values],
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Require exactly one handle and at least one value."""
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
            if not self.lab_values:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "At least one lab value is required to attach results.",
                        self.lab_values,
                    )
                )

        return errors


__exports__ = ("LabReportAttachResults", "LabValue")

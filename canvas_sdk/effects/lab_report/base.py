"""Fluent ``LabReport`` SDK effect: create / update / enter-in-error / attach-results.

A report is identified by a plugin-supplied ``external_id`` handle (stable
across the asynchronous OCR lifecycle — create the report now, attach
values days later) or, once known, the Canvas ``report_id`` (the report's
externally-exposable id, recoverable via the ``LAB_REPORT_CREATED`` event
or a ``LabReport`` data query).

Mirrors the shipped ``Observation`` CRUD effect.
"""

import datetime
import json
from typing import TYPE_CHECKING, Annotated, Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect

if TYPE_CHECKING:
    from canvas_sdk.effects.lab_report.attach_results import LabValue

_MUTABLE_FIELDS = ("report_name", "date_performed")


class LabReport(TrackableFieldsModel):
    """Effect to create, update, enter-in-error, or attach results to a ``LabReport``."""

    class Meta:
        effect_type = "LAB_REPORT"

    report_id: UUID | None = Field(default=None, strict=False)  # Canvas externally-exposable id
    external_id: Annotated[str, Field(max_length=40)] | None = None  # plugin-supplied handle
    patient_id: str | None = None
    report_name: str | None = None  # maps to LabReport.custom_document_name
    date_performed: datetime.datetime | None = None

    def _handle_payload(self) -> dict[str, str]:
        """Serialize just the handle (used by enter_in_error)."""
        if self.report_id:
            return {"report_id": str(self.report_id)}
        return {"external_id": str(self.external_id)}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate per-method requirements for the report lifecycle."""
        errors = super()._get_error_details(method)

        if method == "create":
            if self.report_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "report_id must not be set when creating a lab report.",
                        self.report_id,
                    )
                )
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "patient_id is required when creating a lab report.",
                        self.patient_id,
                    )
                )
            if not self.external_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "external_id is required when creating a lab report (it is the "
                        "plugin's stable handle for later attaching results).",
                        self.external_id,
                    )
                )

        if method in ("update", "enter_in_error") and not (self.report_id or self.external_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    "report_id or external_id is required to reference a lab report.",
                    None,
                )
            )

        if method == "update" and all(getattr(self, f) is None for f in _MUTABLE_FIELDS):
            errors.append(
                self._create_error_detail(
                    "value",
                    "At least one of report_name or date_performed must be set to update "
                    "a lab report.",
                    None,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a lab report, decoupled from its results."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update report metadata (e.g. rename via report_name)."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def enter_in_error(self) -> Effect:
        """Mark the report as entered-in-error.

        Only the report handle (``report_id`` or ``external_id``) is sent;
        any other field on the instance is ignored.
        """
        self._validate_before_effect("enter_in_error")
        return Effect(
            type=f"ENTER_IN_ERROR_{self.Meta.effect_type}",
            payload=json.dumps({"data": self._handle_payload()}),
        )

    def attach_results(self, lab_values: list["LabValue"]) -> Effect:
        """Additively attach lab tests/values to this report.

        Uses this instance's handle (``report_id`` or ``external_id``).
        """
        from canvas_sdk.effects.lab_report.attach_results import _LabReportAttachResults

        return _LabReportAttachResults(
            report_id=self.report_id,
            external_id=self.external_id or "",
            lab_values=lab_values,
        ).apply()


__exports__ = ("LabReport",)

"""Fluent ``LabReport`` SDK effect: create / update / enter-in-error.

A report is identified by a plugin-supplied ``external_id`` handle (stable
across the asynchronous OCR lifecycle — create the report now, attach
values days later) or, once known, the Canvas ``report_id`` (the report's
externally-exposable id, recoverable via the ``LAB_REPORT_CREATED`` event
or a ``LabReport`` data query).

Mirrors the shipped ``Observation`` CRUD effect. Results are attached via
the separate :class:`~canvas_sdk.effects.lab_report.attach_results.LabReportAttachResults`
effect.
"""

import datetime
import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.lab import LabReport as LabReportModel

_HANDLE_FIELDS = ("report_id", "external_id")
_MUTABLE_FIELDS = ("report_name", "date_performed")


class LabReport(TrackableFieldsModel):
    """Effect to create, update, or enter-in-error a ``LabReport``."""

    class Meta:
        effect_type = "LAB_REPORT"

    report_id: str | UUID | None = None  # Canvas externally-exposable id (update/EIE)
    external_id: str | None = None  # plugin-supplied handle
    patient_id: str | None = None
    report_name: str | None = None  # maps to LabReport.custom_document_name
    date_performed: datetime.datetime | None = None

    def _report_exists(self) -> bool:
        """Return True if a report matches the supplied handle."""
        if self.report_id:
            return LabReportModel.objects.filter(id=self.report_id).exists()
        if self.external_id:
            return LabReportModel.objects.filter(external_id=self.external_id).exists()
        return False

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

        if method in ("update", "enter_in_error"):
            if not (self.report_id or self.external_id):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "report_id or external_id is required to reference a lab report.",
                        None,
                    )
                )
            elif not self._report_exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"LabReport not found for {self.report_id or self.external_id}.",
                        self.report_id or self.external_id,
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

        if method == "enter_in_error":
            other_fields = sorted(k for k in self.values if k not in _HANDLE_FIELDS)
            if other_fields:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Only a report handle is allowed when entering a lab report in "
                        f"error. Got: {other_fields}",
                        other_fields,
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

        Only a handle (``report_id`` or ``external_id``) is honored; any
        other field raises a validation error if set.
        """
        self._validate_before_effect("enter_in_error")
        return Effect(
            type=f"ENTER_IN_ERROR_{self.Meta.effect_type}",
            payload=json.dumps({"data": self._handle_payload()}),
        )


__exports__ = ("LabReport",)

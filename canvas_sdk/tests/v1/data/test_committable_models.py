from typing import Any

import pytest

from canvas_sdk.v1.data.assessment import Assessment
from canvas_sdk.v1.data.base import CommittableQuerySetMixin
from canvas_sdk.v1.data.chart_section_review import ChartSectionReview
from canvas_sdk.v1.data.detected_issue import DetectedIssue
from canvas_sdk.v1.data.device import Device
from canvas_sdk.v1.data.goal import Goal
from canvas_sdk.v1.data.imaging import ImagingOrder, ImagingReview
from canvas_sdk.v1.data.immunization import Immunization, ImmunizationStatement
from canvas_sdk.v1.data.lab import LabOrder, LabOrderReason
from canvas_sdk.v1.data.medication_statement import MedicationStatement
from canvas_sdk.v1.data.referral import Referral
from canvas_sdk.v1.data.stop_medication_event import StopMedicationEvent
from canvas_sdk.v1.data.task import NoteTask
from canvas_sdk.v1.data.visual_exam_finding import VisualExamFinding

COMMITTABLE_COMMAND_MODELS = [
    Immunization,
    ImmunizationStatement,
    Goal,
    MedicationStatement,
    Assessment,
    StopMedicationEvent,
    Device,
    DetectedIssue,
    ChartSectionReview,
    VisualExamFinding,
    ImagingOrder,
    ImagingReview,
    LabOrder,
    LabOrderReason,
    NoteTask,
    Referral,
]


@pytest.mark.parametrize("model", COMMITTABLE_COMMAND_MODELS)
def test_command_model_queryset_uses_committable_mixin(model: Any) -> None:
    """Each command model's manager returns a queryset that exposes committed()."""
    assert isinstance(model.objects.all(), CommittableQuerySetMixin)


@pytest.mark.django_db
@pytest.mark.parametrize("model", COMMITTABLE_COMMAND_MODELS)
def test_command_model_committed_resolves_audit_fields(model: Any) -> None:
    """committed() resolves committer/entered_in_error against the model's table.

    Regression test for canvas-plugins#1067, where Immunization and
    ImmunizationStatement declared the committable mixin but lacked the
    committer/entered_in_error fields, so committed() raised a FieldError.
    """
    assert model.objects.committed().count() == 0


@pytest.mark.django_db
def test_immunization_active_uses_committed() -> None:
    """active() delegates to committed() and resolves without a FieldError (#1067)."""
    assert Immunization.objects.active().count() == 0
    assert ImmunizationStatement.objects.active().count() == 0

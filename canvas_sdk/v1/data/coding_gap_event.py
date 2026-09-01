from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class CreateCodingGapEvent(AuditedModel, IdentifiableModel):
    """The anchor for the CreateCodingGap command — records creating a coding gap (DetectedIssue)."""

    class Meta:
        db_table = "canvas_sdk_data_api_createcodinggapevent_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="created_coding_gaps"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="created_coding_gaps"
    )
    detected_issue = models.ForeignKey(
        "v1.DetectedIssue",
        on_delete=models.DO_NOTHING,
        related_name="created_coding_gap_events",
        null=True,
    )


class ValidateCodingGapEvent(AuditedModel, IdentifiableModel):
    """The anchor for the ValidateCodingGap command."""

    class Meta:
        db_table = "canvas_sdk_data_api_validatecodinggapevent_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="validated_coding_gaps"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="validated_coding_gaps"
    )
    detected_issue = models.ForeignKey(
        "v1.DetectedIssue",
        on_delete=models.DO_NOTHING,
        related_name="validated_coding_gap_events",
        null=True,
    )


class AssessCodingGapEvent(AuditedModel, IdentifiableModel):
    """The anchor for the AssessCodingGap command — associates conditions with a coding gap."""

    class Meta:
        db_table = "canvas_sdk_data_api_assesscodinggapevent_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="assessed_coding_gaps"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="assessed_coding_gaps"
    )
    detected_issue = models.ForeignKey(
        "v1.DetectedIssue",
        on_delete=models.DO_NOTHING,
        related_name="assessed_coding_gap_events",
        null=True,
    )
    conditions = models.ManyToManyField(
        "v1.Condition",
        related_name="assessed_coding_gaps",
        blank=True,
        db_table="canvas_sdk_data_api_assesscodinggapevent_conditions_001",
    )


class DeferCodingGapEvent(AuditedModel, IdentifiableModel):
    """The anchor for the DeferCodingGap command."""

    class Meta:
        db_table = "canvas_sdk_data_api_defercodinggapevent_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="deferred_coding_gaps"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="deferred_coding_gaps"
    )
    detected_issue = models.ForeignKey(
        "v1.DetectedIssue",
        on_delete=models.DO_NOTHING,
        related_name="deferred_coding_gap_events",
        null=True,
    )


__exports__ = (
    "AssessCodingGapEvent",
    "CreateCodingGapEvent",
    "DeferCodingGapEvent",
    "ValidateCodingGapEvent",
)

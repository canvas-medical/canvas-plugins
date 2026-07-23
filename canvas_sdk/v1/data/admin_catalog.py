"""Admin-side catalog rows the Notion gap analysis calls out as missing
from the SDK: Label / Queue / Protocol-template / Diagnostic View /
Command Type. These are configuration catalogs (registry-style) distinct
from the patient-level UserSelectedTaskLabel and ClaimLabel records the SDK
already exposes.
"""

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class AdminLabel(TimestampedModel, IdentifiableModel):
    """Administrative Label catalog (distinct from per-task UserSelectedTaskLabel)."""

    class Meta:
        db_table = "canvas_sdk_data_api_adminlabel_001"

    name = models.CharField(max_length=128)
    color = models.CharField(max_length=16, blank=True, default="")
    auto_apply_for_task_types = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=True)


class AdminQueue(TimestampedModel, IdentifiableModel):
    """A task queue (work pool) staff can be routed to."""

    class Meta:
        db_table = "canvas_sdk_data_api_adminqueue_001"

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512, blank=True, default="")
    active = models.BooleanField(default=True)


class AdminProtocolTemplate(TimestampedModel, IdentifiableModel):
    """A clinical protocol template (distinct from PROTOCOL_OVERRIDE on a patient)."""

    class Meta:
        db_table = "canvas_sdk_data_api_adminprotocoltemplate_001"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    payload = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=True)


class AdminDiagnosticView(TimestampedModel, IdentifiableModel):
    """A diagnostic-view (clinical report layout) catalog entry."""

    class Meta:
        db_table = "canvas_sdk_data_api_admindiagnosticview_001"

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, blank=True, default="")
    payload = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=True)


class AdminCommandType(TimestampedModel, IdentifiableModel):
    """A registered custom command type."""

    class Meta:
        db_table = "canvas_sdk_data_api_admincommandtype_001"

    name = models.CharField(max_length=128)
    display = models.CharField(max_length=255, blank=True, default="")
    schema = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=True)


__exports__ = (
    "AdminLabel",
    "AdminQueue",
    "AdminProtocolTemplate",
    "AdminDiagnosticView",
    "AdminCommandType",
)

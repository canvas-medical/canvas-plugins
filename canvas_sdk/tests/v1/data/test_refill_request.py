"""Tests for RefillRequest models and querysets."""

from canvas_sdk.v1.data import RefillRequest as ExportedRefillRequest
from canvas_sdk.v1.data.refill_request import RefillRequest, RefillRequestCoding


def test_refill_request_manager_omits_deleted_filter() -> None:
    """RefillRequest is not an AuditedModel and its view has no `deleted` column, so its
    manager must not inject a ``deleted=False`` filter. Compiling the query would raise
    ``FieldError: Cannot resolve keyword 'deleted'`` if the wrong manager were used.
    """
    sql = str(RefillRequest.objects.all().query)
    assert "deleted" not in sql.lower()


def test_refill_request_patient_filter_compiles() -> None:
    """A patient-scoped query builds valid SQL without referencing `deleted`."""
    sql = str(RefillRequest.objects.filter(patient__id="pat-1").query)
    assert "deleted" not in sql.lower()
    assert "patient" in sql.lower()


def test_refill_request_is_exported() -> None:
    """RefillRequest is re-exported from canvas_sdk.v1.data."""
    assert ExportedRefillRequest is RefillRequest


def test_refill_request_coding_relates_to_refill_request() -> None:
    """RefillRequestCoding points back at RefillRequest via the codings relation."""
    assert RefillRequestCoding._meta.get_field("refill_request").related_model is RefillRequest

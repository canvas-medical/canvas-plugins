"""Tests for RefillRequest models and querysets."""

from typing import Any

import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    PatientFactory,
    PrescriptionFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import RefillRequest as ExportedRefillRequest
from canvas_sdk.v1.data.prescription import Prescription, PrescriptionStatus
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


def _refill_request(**fields: Any) -> RefillRequest:
    """A refill request for a new patient, assigned to a new staff member."""
    return RefillRequest.objects.create(
        patient=PatientFactory.create(), staff=StaffFactory.create(), **fields
    )


def _response(refill_request: RefillRequest, **fields: Any) -> Prescription:
    """A refill response to the request."""
    return PrescriptionFactory.create(
        patient=refill_request.patient, refill_request=refill_request, **fields
    )


@pytest.mark.django_db
def test_pending_keeps_requests_no_sent_response_answered() -> None:
    """A request stays in the queue until a sent response answers it: one with no response, an
    unsent one, one that failed to reach the pharmacy, or one entered in error before the
    pharmacy received it all stay.
    """
    user = CanvasUserFactory.create()
    untouched = _refill_request()
    unsent = _refill_request()
    _response(unsent, committer=None)
    failed = _refill_request()
    _response(failed, committer=user, status=PrescriptionStatus.ERROR)
    entered_in_error = _refill_request()
    _response(entered_in_error, committer=user, entered_in_error=user, message_id="")

    assert set(RefillRequest.objects.pending()) == {untouched, unsent, failed, entered_in_error}


@pytest.mark.django_db
def test_pending_drops_ignored_and_answered_requests() -> None:
    """Ignored requests, and requests a sent response answered, leave the queue, including one
    whose first response failed and whose second was sent, and one whose response the pharmacy
    received before it was entered in error.
    """
    user = CanvasUserFactory.create()
    _refill_request(ignored=True)
    answered = _refill_request()
    _response(answered, committer=user, status=PrescriptionStatus.PENDING)
    retried = _refill_request()
    _response(retried, committer=user, status=PrescriptionStatus.ERROR)
    _response(retried, committer=user, status=PrescriptionStatus.DELIVERED)
    received_then_entered_in_error = _refill_request()
    _response(
        received_then_entered_in_error,
        committer=user,
        status=PrescriptionStatus.DELIVERED,
        entered_in_error=user,
        message_id="a1b2c3",
    )

    assert not RefillRequest.objects.pending().exists()

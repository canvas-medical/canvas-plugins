import factory
import pytest
from django.db import models

from canvas_sdk.test_utils.factories import (
    ContentTypeFactory,
    ImagingOrderFactory,
    LabOrderFactory,
    PatientFactory,
    ProcedureFactory,
    ReferralFactory,
    ServiceRequestCategoryCodingFactory,
    ServiceRequestCodingFactory,
    ServiceRequestFactory,
    ServiceRequestReasonConditionFactory,
)
from canvas_sdk.v1.data import (
    ServiceRequest,
    ServiceRequestCategoryCoding,
    ServiceRequestCoding,
    ServiceRequestReasonCondition,
    ServiceRequestStatus,
)


@pytest.mark.django_db
def test_service_request_is_found_by_id_and_status() -> None:
    """A service request is found by its id and status, and its fields round-trip."""
    service_request = ServiceRequestFactory.create(status=ServiceRequestStatus.DRAFT)
    ServiceRequestFactory.create(status=ServiceRequestStatus.COMPLETED)

    fetched = ServiceRequest.objects.get(id=service_request.id)

    assert fetched.dbid == service_request.dbid
    assert fetched.status == ServiceRequestStatus.DRAFT
    assert fetched.authored_on == service_request.authored_on
    assert list(ServiceRequest.objects.filter(status=ServiceRequestStatus.DRAFT)) == [fetched]


@pytest.mark.django_db
def test_for_patient_returns_only_that_patients_service_requests() -> None:
    """for_patient filters by the patient's public id."""
    patient = PatientFactory.create()
    mine = ServiceRequestFactory.create(patient=patient)
    ServiceRequestFactory.create()

    assert list(ServiceRequest.objects.for_patient(patient.id)) == [mine]


@pytest.mark.django_db
def test_service_request_resolves_patient_and_requester() -> None:
    """The patient and requester foreign keys resolve, with service_requests as the reverse."""
    service_request = ServiceRequestFactory.create()
    ServiceRequestFactory.create()

    fetched = ServiceRequest.objects.get(id=service_request.id)

    assert fetched.patient == service_request.patient
    assert fetched.requester is not None
    assert fetched.requester == service_request.requester
    assert list(fetched.patient.service_requests.all()) == [fetched]
    assert list(fetched.requester.service_requests.all()) == [fetched]


@pytest.mark.django_db
def test_requester_is_optional() -> None:
    """A service request can have no requester."""
    service_request = ServiceRequestFactory.create(requester=None)

    assert ServiceRequest.objects.get(id=service_request.id).requester is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("model_name", "order_factory"),
    [
        ("imagingorder", ImagingOrderFactory),
        ("laborder", LabOrderFactory),
        ("referral", ReferralFactory),
        ("procedure", ProcedureFactory),
    ],
)
def test_requested_service_resolves_the_wrapped_order(
    model_name: str, order_factory: type[factory.django.DjangoModelFactory[models.Model]]
) -> None:
    """requested_service resolves the content type and object id to the SDK order."""
    order = order_factory.create()
    service_request = ServiceRequestFactory.create(
        requested_service_type=ContentTypeFactory.create(app_label="api", model=model_name),
        requested_service_object_id=order.pk,
    )

    assert ServiceRequest.objects.get(id=service_request.id).requested_service == order


@pytest.mark.django_db
def test_requested_service_is_none_without_a_link_or_for_an_unknown_type() -> None:
    """requested_service is None when unlinked or when the content type has no SDK model."""
    unlinked = ServiceRequestFactory.create()
    unknown = ServiceRequestFactory.create(
        requested_service_type=ContentTypeFactory.create(app_label="api", model="note"),
        requested_service_object_id=1,
    )

    assert unlinked.requested_service is None
    assert unknown.requested_service is None


@pytest.mark.django_db
def test_category_codings_and_codings_are_reverse_accessors() -> None:
    """Category codings and service codings hang off the service request."""
    service_request = ServiceRequestFactory.create()
    category = ServiceRequestCategoryCodingFactory.create(
        service_request=service_request, code="71388002", display="Procedure"
    )
    coding = ServiceRequestCodingFactory.create(service_request=service_request, code="24627-2")
    ServiceRequestCodingFactory.create()

    assert list(service_request.category_codings.all()) == [category]
    assert list(service_request.codings.all()) == [coding]
    fetched_category = ServiceRequestCategoryCoding.objects.get(dbid=category.dbid)
    assert (fetched_category.code, fetched_category.display) == ("71388002", "Procedure")
    fetched_coding = ServiceRequestCoding.objects.get(dbid=coding.dbid)
    assert fetched_coding.code == "24627-2"
    assert fetched_coding.service_request == service_request


@pytest.mark.django_db
def test_reason_conditions_link_service_requests_and_conditions() -> None:
    """Reason conditions are reachable from both sides, directly and through the join table."""
    reason = ServiceRequestReasonConditionFactory.create()
    service_request = reason.service_request
    condition = reason.condition
    ServiceRequestReasonConditionFactory.create()

    fetched = ServiceRequestReasonCondition.objects.get(dbid=reason.dbid)

    assert fetched.service_request == service_request
    assert fetched.condition == condition
    assert fetched.condition.patient == service_request.patient
    assert list(service_request.reason_conditions.all()) == [fetched]
    assert list(condition.service_request_reasons.all()) == [fetched]
    assert list(service_request.conditions.all()) == [condition]
    assert list(condition.service_requests.all()) == [service_request]

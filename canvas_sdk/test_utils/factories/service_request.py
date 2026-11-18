import datetime

import factory

from canvas_sdk.v1.data import (
    ServiceRequest,
    ServiceRequestCategoryCoding,
    ServiceRequestCoding,
    ServiceRequestReasonCondition,
    ServiceRequestStatus,
)


class ServiceRequestFactory(factory.django.DjangoModelFactory[ServiceRequest]):
    """Factory for creating a ServiceRequest."""

    class Meta:
        model = ServiceRequest

    status = ServiceRequestStatus.ACTIVE
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    requester = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    authored_on = factory.Faker("date_time", tzinfo=datetime.UTC)
    requested_service_type = None
    requested_service_object_id = None


class ServiceRequestCategoryCodingFactory(
    factory.django.DjangoModelFactory[ServiceRequestCategoryCoding]
):
    """Factory for creating a ServiceRequestCategoryCoding."""

    class Meta:
        model = ServiceRequestCategoryCoding

    service_request = factory.SubFactory(ServiceRequestFactory)
    system = "http://snomed.info/sct"
    code = "363679005"
    display = "Imaging"


class ServiceRequestCodingFactory(factory.django.DjangoModelFactory[ServiceRequestCoding]):
    """Factory for creating a ServiceRequestCoding."""

    class Meta:
        model = ServiceRequestCoding

    service_request = factory.SubFactory(ServiceRequestFactory)
    system = "http://loinc.org"
    code = factory.Sequence(lambda n: f"{n:05d}-0")
    display = factory.Faker("text", max_nb_chars=100)


class ServiceRequestReasonConditionFactory(
    factory.django.DjangoModelFactory[ServiceRequestReasonCondition]
):
    """Factory for creating a ServiceRequestReasonCondition."""

    class Meta:
        model = ServiceRequestReasonCondition

    service_request = factory.SubFactory(ServiceRequestFactory)
    condition = factory.SubFactory(
        "canvas_sdk.test_utils.factories.ConditionFactory",
        patient=factory.SelfAttribute("..service_request.patient"),
    )

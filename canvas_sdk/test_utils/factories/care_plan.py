import factory

from canvas_sdk.v1.data import CarePlan, CarePlanCoding, CarePlanIntent, CarePlanStatus


class CarePlanCodingFactory(factory.django.DjangoModelFactory[CarePlanCoding]):
    """Factory for creating a CarePlanCoding."""

    class Meta:
        model = CarePlanCoding

    system = "http://snomed.info/sct"
    code = "734163000"
    display = "Care plan"


class CarePlanFactory(factory.django.DjangoModelFactory[CarePlan]):
    """Factory for creating a CarePlan."""

    class Meta:
        model = CarePlan

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    status = CarePlanStatus.ACTIVE
    intent = CarePlanIntent.PLAN
    category = factory.SubFactory(CarePlanCodingFactory)

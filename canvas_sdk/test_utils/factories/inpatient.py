import factory

from canvas_sdk.v1.data import InpatientFacility, InpatientStay


class InpatientFacilityFactory(factory.django.DjangoModelFactory[InpatientFacility]):
    """Factory for creating an InpatientFacility."""

    class Meta:
        model = InpatientFacility

    name = factory.Faker("company")
    npi_number = factory.Sequence(lambda n: f"{1000000000 + n}")


class InpatientStayFactory(factory.django.DjangoModelFactory[InpatientStay]):
    """Factory for creating an InpatientStay."""

    class Meta:
        model = InpatientStay

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    inpatient_facility = factory.SubFactory(InpatientFacilityFactory)
    room_number = "101"

import datetime

import factory
from factory.fuzzy import FuzzyDate

from canvas_sdk.test_utils.factories.facility import FacilityFactory
from canvas_sdk.test_utils.factories.user import CanvasUserFactory
from canvas_sdk.v1.data import (
    Patient,
    PatientAddress,
    PatientContactPerson,
    PatientFacilityAddress,
    PatientKnownLocation,
    PatientParentGuardian,
    PatientPhoto,
    PatientTribalAffiliationCoding,
)


class PatientAddressFactory(factory.django.DjangoModelFactory[PatientAddress]):
    """Factory for creating a PatientAddress."""

    class Meta:
        model = PatientAddress

    line1 = "1234 Main Street"
    line2 = "Apt 3"
    city = "San Francisco"
    district = "Sunset"
    state_code = "CA"
    postal_code = "94112"
    country = "USA"


class PatientFactory(factory.django.DjangoModelFactory[Patient]):
    """Factory for creating a Patient."""

    class Meta:
        model = Patient

    birth_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=100 * 365),
        end_date=datetime.date.today() - datetime.timedelta(days=10 * 365),
    )
    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    addresses = factory.RelatedFactory(PatientAddressFactory, "patient")
    user = factory.SubFactory(CanvasUserFactory)


class PatientPhotoFactory(factory.django.DjangoModelFactory[PatientPhoto]):
    """Factory for creating PatientPhoto."""

    class Meta:
        model = PatientPhoto

    url = ""
    patient = factory.SubFactory(PatientFactory)


class PatientFacilityAddressFactory(factory.django.DjangoModelFactory[PatientFacilityAddress]):
    """Factory for creating a PatientFacilityAddress."""

    class Meta:
        model = PatientFacilityAddress

    facility = factory.SubFactory(FacilityFactory)
    patient = factory.SubFactory(PatientFactory)
    room_number = factory.Faker("building_number")


class PatientContactPersonFactory(factory.django.DjangoModelFactory[PatientContactPerson]):
    """Factory for creating one of a patient's contacts."""

    class Meta:
        model = PatientContactPerson

    patient = factory.SubFactory(PatientFactory)
    name = factory.Faker("name")
    email = factory.Faker("email")


class PatientKnownLocationFactory(factory.django.DjangoModelFactory[PatientKnownLocation]):
    """Factory for creating a PatientKnownLocation."""

    class Meta:
        model = PatientKnownLocation

    patient = factory.SubFactory(PatientFactory)
    originator = factory.SubFactory(CanvasUserFactory)
    known_location = factory.Faker("street_address")


class PatientParentGuardianFactory(factory.django.DjangoModelFactory[PatientParentGuardian]):
    """Factory for creating a PatientParentGuardian."""

    class Meta:
        model = PatientParentGuardian

    patient = factory.SubFactory(PatientFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class PatientTribalAffiliationCodingFactory(
    factory.django.DjangoModelFactory[PatientTribalAffiliationCoding]
):
    """Factory for creating a PatientTribalAffiliationCoding."""

    class Meta:
        model = PatientTribalAffiliationCoding

    patient = factory.SubFactory(PatientFactory)
    system = "http://terminology.hl7.org/CodeSystem/v3-TribalEntityUS"
    code = "40"
    display = "Cherokee Nation"

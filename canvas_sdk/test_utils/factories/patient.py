import datetime

import factory
from factory.fuzzy import FuzzyDate

from canvas_sdk.test_utils.factories.user import CanvasUserFactory
from canvas_sdk.v1.data import Patient, PatientAddress


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

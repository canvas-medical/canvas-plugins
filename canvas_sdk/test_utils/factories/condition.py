"""Factories for Condition and ConditionCoding models."""

from datetime import date

import factory

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data.condition import ClinicalStatus, Condition, ConditionCoding


class ConditionFactory(factory.django.DjangoModelFactory[Condition]):
    """Factory for creating a Condition."""

    class Meta:
        model = Condition

    patient = factory.SubFactory(PatientFactory)
    onset_date = factory.LazyFunction(date.today)
    resolution_date = None
    clinical_status = ClinicalStatus.ACTIVE
    surgical = False
    deleted = False


class ConditionCodingFactory(factory.django.DjangoModelFactory[ConditionCoding]):
    """Factory for creating a ConditionCoding."""

    class Meta:
        model = ConditionCoding

    condition = factory.SubFactory(ConditionFactory)
    system = "http://snomed.info/sct"
    code = factory.Faker("numerify", text="########")
    display = factory.Faker("sentence", nb_words=3)

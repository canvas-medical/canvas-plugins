"""Factories for condition-related models."""

import arrow
import factory

from canvas_sdk.v1.data.condition import ClinicalStatus, Condition, ConditionCoding


class ConditionFactory(factory.django.DjangoModelFactory[Condition]):
    """Factory for creating Condition test data."""

    class Meta:
        model = Condition

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    onset_date = factory.LazyFunction(lambda: arrow.now().date())
    deleted = False
    clinical_status = ClinicalStatus.ACTIVE
    resolution_date = factory.LazyFunction(lambda: arrow.get("9999-12-31").date())
    surgical = True


class ConditionCodingFactory(factory.django.DjangoModelFactory[ConditionCoding]):
    """Factory for creating ConditionCoding test data."""

    class Meta:
        model = ConditionCoding

    condition = factory.SubFactory(ConditionFactory)
    system = "http://snomed.info/sct"
    code = "12345"
    display = "Test Condition"

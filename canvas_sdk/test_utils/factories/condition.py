import datetime

import factory

from canvas_sdk.v1.data import Condition, ConditionCategoryCoding
from canvas_sdk.v1.data.condition import ClinicalStatus


class ConditionFactory(factory.django.DjangoModelFactory[Condition]):
    """Factory for creating a Condition."""

    class Meta:
        model = Condition

    deleted = False
    onset_date = datetime.date(2024, 1, 1)
    resolution_date = datetime.date(2024, 1, 1)
    clinical_status = ClinicalStatus.ACTIVE
    notes = ""
    surgical = False


class ConditionCategoryCodingFactory(factory.django.DjangoModelFactory[ConditionCategoryCoding]):
    """Factory for creating a ConditionCategoryCoding."""

    class Meta:
        model = ConditionCategoryCoding

    condition = factory.SubFactory(ConditionFactory)
    system = "http://terminology.hl7.org/CodeSystem/condition-category"
    code = "problem-list-item"
    display = "Problem List Item"

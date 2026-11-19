import datetime

import factory

from canvas_sdk.v1.data import Condition, ConditionCategoryCoding
from canvas_sdk.v1.data.condition import ClinicalStatus


class ConditionFactory(factory.django.DjangoModelFactory[Condition]):
    """Factory for creating a Condition."""

    class Meta:
        model = Condition

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    committer = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    deleted = False
    onset_date = datetime.date(2020, 1, 1)
    # sentinel: the SDK field is non-nullable, while home-app stores NULL for an active condition
    resolution_date = datetime.date(2099, 12, 31)
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

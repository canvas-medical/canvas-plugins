import factory
from django.utils import timezone

from canvas_sdk.v1.data import (
    Campaign,
    Intervention,
    SuspectHCC,
    SuspectHCCKind,
    SuspectHCCStatus,
)


class SuspectHCCFactory(factory.django.DjangoModelFactory[SuspectHCC]):
    """Factory for creating a SuspectHCC."""

    class Meta:
        model = SuspectHCC

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    status = SuspectHCCStatus.ACTIVE
    hcc_description = "End-stage liver disease"
    hcc_code = "27"
    reasons = factory.LazyFunction(lambda: ["Condition: End-stage liver disease"])
    previous_condition = ""
    kind = SuspectHCCKind.IMPLIED_BY_CLINICAL_DATA


class CampaignFactory(factory.django.DjangoModelFactory[Campaign]):
    """Factory for creating a Campaign."""

    class Meta:
        model = Campaign

    title = factory.Faker("sentence", nb_words=3)
    description = None
    closed_at = None
    protocol_id = factory.Sequence(lambda n: n + 1)
    work_list = False
    total_patients_on_closure = 0
    satisfied_patients_on_closure = 0


class InterventionFactory(factory.django.DjangoModelFactory[Intervention]):
    """Factory for creating an Intervention."""

    class Meta:
        model = Intervention

    campaign = factory.SubFactory(CampaignFactory)
    template = factory.SubFactory("canvas_sdk.test_utils.factories.LetterTemplateFactory")
    start_delivery = factory.LazyFunction(timezone.now)
    author = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")

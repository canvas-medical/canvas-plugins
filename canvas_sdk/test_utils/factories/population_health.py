import factory
from django.utils import timezone

from canvas_sdk.v1.data import Campaign, Intervention


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

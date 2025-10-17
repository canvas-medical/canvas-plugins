import factory

from canvas_sdk.v1.data import Claim, ClaimQueue


class ClaimQueueFactory(factory.django.DjangoModelFactory[ClaimQueue]):
    """Factory for creating ClaimQueue."""

    class Meta:
        model = ClaimQueue
        django_get_or_create = ("queue_sort_ordering",)

    queue_sort_ordering = 5
    name = "Claim: Filed"


class ClaimFactory(factory.django.DjangoModelFactory[Claim]):
    """Factory for creating Claim."""

    class Meta:
        model = Claim

    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    current_queue = factory.SubFactory(ClaimQueueFactory)

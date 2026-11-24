import factory

from canvas_sdk.v1.data.snapshot import Snapshot


class SnapshotFactory(factory.django.DjangoModelFactory[Snapshot]):
    """Factory for creating a Snapshot."""

    class Meta:
        model = Snapshot

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    title = factory.Faker("sentence", nb_words=2)
    description = factory.Faker("sentence")

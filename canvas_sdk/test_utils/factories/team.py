import factory

from canvas_sdk.v1.data.team import Team


class TeamFactory(factory.django.DjangoModelFactory[Team]):
    """Factory for creating a Team."""

    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Test Team {n}")
    responsibilities: list[str] = []

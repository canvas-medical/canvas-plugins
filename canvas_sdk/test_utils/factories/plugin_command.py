import factory

from canvas_sdk.v1.data import PluginCommand


class PluginCommandFactory(factory.django.DjangoModelFactory[PluginCommand]):
    """Factory for creating a PluginCommand."""

    class Meta:
        model = PluginCommand

    name = factory.Faker("word")
    command_key = factory.Faker("word")
    schema_key = factory.Sequence(lambda n: f"command_schema_key_{n}")
    label = factory.Faker("word")
    section = "subjective"

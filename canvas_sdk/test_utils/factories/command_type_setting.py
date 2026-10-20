import factory

from canvas_sdk.v1.data import CommandTypeSetting


class CommandTypeSettingFactory(factory.django.DjangoModelFactory[CommandTypeSetting]):
    """Factory for creating a CommandTypeSetting."""

    class Meta:
        model = CommandTypeSetting

    schema_key = factory.Sequence(lambda n: f"command{n}")
    active = True

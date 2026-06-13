import factory

from canvas_sdk.v1.data import DjangoContentType


class DjangoContentTypeFactory(factory.django.DjangoModelFactory[DjangoContentType]):
    """Factory for creating a DjangoContentType."""

    class Meta:
        model = DjangoContentType

    app_label = "api"
    model = factory.Sequence(lambda n: f"model_{n}")

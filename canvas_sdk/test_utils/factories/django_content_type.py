import factory

from canvas_sdk.v1.data import ContentType


class ContentTypeFactory(factory.django.DjangoModelFactory[ContentType]):
    """Factory for creating a Django ContentType."""

    class Meta:
        model = ContentType

    app_label = "api"
    model = factory.Sequence(lambda n: f"model_{n}")

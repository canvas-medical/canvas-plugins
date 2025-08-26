import factory

from canvas_sdk.v1.data import CanvasUser


class CanvasUserFactory(factory.django.DjangoModelFactory[CanvasUser]):
    """Factory for creating a CanvasUser."""

    class Meta:
        model = CanvasUser

    email = factory.Faker("email")
    phone_number = factory.Faker("phone_number")

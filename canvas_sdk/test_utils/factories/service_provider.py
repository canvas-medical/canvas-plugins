import factory

from canvas_sdk.v1.data import ServiceProvider


class ServiceProviderFactory(factory.django.DjangoModelFactory[ServiceProvider]):
    """Factory for creating ServiceProvider."""

    class Meta:
        model = ServiceProvider

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    business_fax = factory.Faker("phone_number")
    business_phone = factory.Faker("phone_number")
    business_address = factory.Faker("address")
    specialty = factory.Faker("job")
    practice_name = factory.Faker("company")
    notes = factory.Faker("text", max_nb_chars=200)

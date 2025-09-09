import factory

from canvas_sdk.v1.data import Facility


class FacilityFactory(factory.django.DjangoModelFactory[Facility]):
    """Factory for creating a Facility."""

    class Meta:
        model = Facility

    name = factory.Faker("company")
    npi_number = factory.Faker("numerify", text="##########")  # 10 digit NPI number
    phone_number = factory.Faker("numerify", text="##########")  # 10 digit phone number
    active = True
    line1 = factory.Faker("street_address")
    line2 = factory.Faker("secondary_address")
    city = factory.Faker("city")
    district = factory.Faker("city_suffix")
    state_code = factory.Faker("state_abbr")
    postal_code = factory.Faker("postcode")

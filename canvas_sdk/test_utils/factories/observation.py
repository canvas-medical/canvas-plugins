import factory

from canvas_sdk.v1.data import ObservationComponent, ObservationComponentValueCoding


class ObservationComponentFactory(factory.django.DjangoModelFactory[ObservationComponent]):
    """Factory for creating an ObservationComponent."""

    class Meta:
        model = ObservationComponent

    observation = None
    value_quantity = ""
    value_quantity_unit = ""
    name = factory.Faker("word")


class ObservationComponentValueCodingFactory(
    factory.django.DjangoModelFactory[ObservationComponentValueCoding]
):
    """Factory for creating an ObservationComponentValueCoding."""

    class Meta:
        model = ObservationComponentValueCoding

    observation_component = factory.SubFactory(ObservationComponentFactory)
    system = "http://snomed.info/sct"
    code = factory.Faker("numerify", text="#########")
    display = factory.Faker("text", max_nb_chars=200)

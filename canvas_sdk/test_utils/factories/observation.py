import factory
from django.utils import timezone

from canvas_sdk.v1.data.observation import (
    Observation,
    ObservationCoding,
    ObservationComponent,
    ObservationComponentCoding,
    ObservationValueCoding,
)


class ObservationFactory(factory.django.DjangoModelFactory[Observation]):
    """Factory for creating Observation."""

    class Meta:
        model = Observation

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    category = "vital-signs"
    units = ""
    value = ""
    note_id = 0
    name = factory.Faker("word")
    effective_datetime = factory.LazyFunction(timezone.now)


class ObservationCodingFactory(factory.django.DjangoModelFactory[ObservationCoding]):
    """Factory for creating ObservationCoding."""

    class Meta:
        model = ObservationCoding

    observation = factory.SubFactory(ObservationFactory)
    code = factory.Faker("bothify", text="########")
    display = factory.Faker("sentence", nb_words=4)
    system = "http://snomed.info/sct"


class ObservationComponentFactory(factory.django.DjangoModelFactory[ObservationComponent]):
    """Factory for creating ObservationComponent."""

    class Meta:
        model = ObservationComponent

    observation = factory.SubFactory(ObservationFactory)
    value_quantity = ""
    value_quantity_unit = ""
    name = factory.Faker("word")


class ObservationComponentCodingFactory(
    factory.django.DjangoModelFactory[ObservationComponentCoding]
):
    """Factory for creating ObservationComponentCoding."""

    class Meta:
        model = ObservationComponentCoding

    observation_component = factory.SubFactory(ObservationComponentFactory)
    code = factory.Faker("bothify", text="########")
    display = factory.Faker("sentence", nb_words=4)
    system = "http://snomed.info/sct"


class ObservationValueCodingFactory(factory.django.DjangoModelFactory[ObservationValueCoding]):
    """Factory for creating ObservationValueCoding."""

    class Meta:
        model = ObservationValueCoding

    observation = factory.SubFactory(ObservationFactory)
    code = factory.Faker("bothify", text="########")
    display = factory.Faker("sentence", nb_words=4)
    system = "http://snomed.info/sct"

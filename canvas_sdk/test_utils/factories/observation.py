import arrow
import factory

from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.v1.data.observation import (
    Observation,
    ObservationCoding,
    ObservationComponent,
    ObservationComponentCoding,
    ObservationValueCoding,
)


class ObservationFactory(factory.django.DjangoModelFactory[Observation]):
    """Factory for creating Observation test data."""

    class Meta:
        model = Observation

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    is_member_of = None
    category = "survey"
    units = ""
    value = ""
    note_id = factory.Sequence(lambda n: n + 1)
    name = "Test Observation"
    effective_datetime = factory.LazyFunction(lambda: arrow.now().datetime)
    deleted = False


class ObservationCodingFactory(factory.django.DjangoModelFactory[ObservationCoding]):
    """Factory for creating ObservationCoding test data."""

    class Meta:
        model = ObservationCoding

    observation = factory.SubFactory(ObservationFactory)
    system = CodeSystems.SNOMED
    code = "12345"
    display = "Test Observation Coding"
    version = ""
    user_selected = False


class ObservationComponentFactory(factory.django.DjangoModelFactory[ObservationComponent]):
    """Factory for creating ObservationComponent test data."""

    class Meta:
        model = ObservationComponent

    observation = factory.SubFactory(ObservationFactory)
    value_quantity = ""
    value_quantity_unit = ""
    name = "Test Component"


class ObservationComponentCodingFactory(
    factory.django.DjangoModelFactory[ObservationComponentCoding]
):
    """Factory for creating ObservationComponentCoding test data."""

    class Meta:
        model = ObservationComponentCoding

    observation_component = factory.SubFactory(ObservationComponentFactory)
    system = CodeSystems.SNOMED
    code = "12345"
    display = "Test Component Coding"
    version = ""
    user_selected = False


class ObservationValueCodingFactory(factory.django.DjangoModelFactory[ObservationValueCoding]):
    """Factory for creating ObservationValueCoding test data."""

    class Meta:
        model = ObservationValueCoding

    observation = factory.SubFactory(ObservationFactory)
    system = CodeSystems.SNOMED
    code = "12345"
    display = "Test Value"
    version = ""
    user_selected = False

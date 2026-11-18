import pytest

from canvas_sdk.test_utils.factories import (
    ObservationComponentFactory,
    ObservationComponentValueCodingFactory,
)
from canvas_sdk.v1.data import ObservationComponentValueCoding


@pytest.mark.django_db
def test_observation_component_value_codings_return_only_its_codings() -> None:
    """ObservationComponent.value_codings returns only that component's codings."""
    parent = ObservationComponentFactory.create()
    coding = ObservationComponentValueCodingFactory.create(observation_component=parent)
    ObservationComponentValueCodingFactory.create()

    assert list(parent.value_codings.all()) == [coding]


@pytest.mark.django_db
def test_observation_component_value_coding_resolves_to_its_observation_component() -> None:
    """The observation_component foreign key resolves to the parent ObservationComponent."""
    parent = ObservationComponentFactory.create()
    coding = ObservationComponentValueCodingFactory.create(observation_component=parent)

    fetched = ObservationComponentValueCoding.objects.get(dbid=coding.dbid)

    assert fetched.observation_component == parent

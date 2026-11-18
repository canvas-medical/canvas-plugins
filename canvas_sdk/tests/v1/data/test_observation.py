import pytest
from django.utils import timezone

from canvas_sdk.test_utils.factories import (
    ObservationComponentFactory,
    ObservationComponentValueCodingFactory,
)
from canvas_sdk.v1.data import Observation, ObservationComponentValueCoding


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


def test_observation_component_value_coding_observation_component_is_required() -> None:
    """The observation_component foreign key is required, matching the NOT NULL column it reads."""
    assert ObservationComponentValueCoding._meta.get_field("observation_component").null is False


@pytest.mark.django_db
def test_observation_reaches_component_value_codings() -> None:
    """An observation's component value codings are reachable through its components."""
    observation = Observation.objects.create(
        category="laboratory",
        units="",
        value="",
        note_id=1,
        name="Urinalysis",
        effective_datetime=timezone.now(),
    )
    component = ObservationComponentFactory.create(observation=observation)
    coding = ObservationComponentValueCodingFactory.create(observation_component=component)
    ObservationComponentValueCodingFactory.create()

    codings = [c for comp in observation.components.all() for c in comp.value_codings.all()]

    assert codings == [coding]

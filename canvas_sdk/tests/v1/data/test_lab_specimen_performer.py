import pytest
from django.utils import timezone

from canvas_sdk.test_utils.factories import (
    LabOrderFactory,
    LabOrderSpecimenFactory,
    LabValueFactory,
    LabValuePerformerFactory,
)
from canvas_sdk.v1.data import LabOrderSpecimen, LabValue, Observation


@pytest.mark.django_db
def test_lab_order_specimen_reads_its_order_and_collection() -> None:
    """A specimen is found by order and reads its type, quantity and collection time."""
    order = LabOrderFactory.create()
    collected = timezone.now()
    specimen = LabOrderSpecimenFactory.create(
        order=order,
        specimen_type="Serum",
        quantity=2.5,
        units="mL",
        source="Venous blood",
        collection_date_time=collected,
    )
    LabOrderSpecimenFactory.create()

    fetched = LabOrderSpecimen.objects.get(order=order)

    assert fetched.id == specimen.id
    assert fetched.specimen_type == "Serum"
    assert fetched.quantity == 2.5
    assert fetched.units == "mL"
    assert fetched.source == "Venous blood"
    assert fetched.collection_date_time == collected
    assert list(order.specimens.all()) == [fetched]


@pytest.mark.django_db
def test_observation_reads_its_specimen() -> None:
    """An observation resolves its specimen, and the specimen lists the observation."""
    specimen = LabOrderSpecimenFactory.create()
    observation = Observation.objects.create(
        category="laboratory",
        units="",
        value="",
        note_id=1,
        name="Glucose",
        effective_datetime=timezone.now(),
        specimen=specimen,
    )

    assert Observation.objects.get(id=observation.id).specimen == specimen
    assert list(specimen.observations.all()) == [observation]


@pytest.mark.django_db
def test_lab_value_reads_its_performer() -> None:
    """A lab value resolves the lab that performed it, and the performer lists the value."""
    performer = LabValuePerformerFactory.create(
        name="Acme Reference Lab", ordinal=1, city="Springfield", phone="5555550100"
    )
    value = LabValueFactory.create(performer=performer)
    LabValueFactory.create()

    fetched = LabValue.objects.get(id=value.id)

    assert fetched.performer == performer
    assert fetched.performer is not None
    assert fetched.performer.name == "Acme Reference Lab"
    assert fetched.performer.ordinal == 1
    assert fetched.performer.city == "Springfield"
    assert fetched.performer.phone == "5555550100"
    assert list(performer.values.all()) == [fetched]

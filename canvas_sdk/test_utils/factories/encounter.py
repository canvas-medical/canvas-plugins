import factory

from canvas_sdk.v1.data import Encounter
from canvas_sdk.v1.data.encounter import EncounterMedium, EncounterState


class EncounterFactory(factory.django.DjangoModelFactory[Encounter]):
    """Factory for creating Encounter."""

    class Meta:
        model = Encounter

    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    medium = EncounterMedium.OFFICE
    state = EncounterState.CONCLUDED
    start_time = factory.LazyAttribute(lambda obj: obj.note.datetime_of_service)
    end_time = factory.LazyAttribute(lambda obj: obj.note.datetime_of_service)

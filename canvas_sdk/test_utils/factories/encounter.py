import factory
from django.utils import timezone

from canvas_sdk.v1.data.encounter import Encounter, EncounterMedium, EncounterState

from .note import NoteFactory


class EncounterFactory(factory.django.DjangoModelFactory[Encounter]):
    """Factory for creating an Encounter."""

    class Meta:
        model = Encounter

    note = factory.SubFactory(NoteFactory)
    medium = EncounterMedium.OFFICE
    state = EncounterState.STARTED
    start_time = timezone.now()

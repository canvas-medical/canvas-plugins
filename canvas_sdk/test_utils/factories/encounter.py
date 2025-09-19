import factory
from factory.fuzzy import FuzzyChoice

from canvas_sdk.v1.data.encounter import Encounter, EncounterMedium, EncounterState

from .note import NoteFactory


class EncounterFactory(factory.django.DjangoModelFactory[Encounter]):
    """Factory for creating an Encounter."""

    class Meta:
        model = Encounter

    note = factory.SubFactory(NoteFactory)
    created = factory.Faker("date_time_between", start_date="-2d", end_date="-1d")
    modified = factory.Faker("date_time_between", start_date="-1d", end_date="0d")
    medium = FuzzyChoice(EncounterMedium.choices, getter=lambda c: c[0])
    state = FuzzyChoice(EncounterState.choices, getter=lambda c: c[0])
    start_time = factory.Faker("date_time_between", start_date="+3d", end_date="+4d")
    end_time = factory.Faker("date_time_between", start_date="+4d", end_date="+5d")

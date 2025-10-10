from typing import Any

import factory

from canvas_sdk.v1.data import Note, NoteStateChangeEvent
from canvas_sdk.v1.data.note import NoteStates


class NoteFactory(factory.django.DjangoModelFactory[Note]):
    """Factory for creating Note."""

    class Meta:
        model = Note

    location = factory.SubFactory("canvas_sdk.test_utils.factories.PracticeLocationFactory")
    originator = factory.SelfAttribute("provider.user")
    provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")

    @factory.post_generation
    def create_initial_state_change_event(self, create: Any, extracted: Any, **kwargs: Any) -> None:
        """Create an initial NoteStateChangeEvent when a Note is created."""
        if not create:
            return

        NoteStateChangeEventFactory.create(note=self, state=NoteStates.NEW)


class NoteStateChangeEventFactory(factory.django.DjangoModelFactory[NoteStateChangeEvent]):
    """Factory for creating NoteStateChangeEvent."""

    class Meta:
        model = NoteStateChangeEvent

    note = factory.SubFactory(NoteFactory)
    state = NoteStates.NEW
    originator = factory.SelfAttribute("note.originator")

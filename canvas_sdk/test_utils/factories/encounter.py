import factory
from django.utils import timezone

from canvas_sdk.v1.data.encounter import Encounter, EncounterMedium, EncounterState


class EncounterFactory(factory.django.DjangoModelFactory[Encounter]):
    """Factory for creating Encounter.

    Default: Creates an in-progress office visit.

    Traits:
        State traits (mutually exclusive):
            - concluded: Concluded encounter with end_time set
            - cancelled: Cancelled encounter
            - planned: Planned/scheduled encounter (no start_time)

        Medium traits (mutually exclusive):
            - video: Video/telehealth visit
            - voice: Telephone visit
            - home: Home visit
            - lab: Lab visit
            - offsite: Other offsite visit

    Examples:
        # Default office visit in progress
        EncounterFactory()

        # Concluded video visit
        EncounterFactory(concluded=True, video=True)

        # Planned home visit
        EncounterFactory(planned=True, home=True)

        # Custom state/medium
        EncounterFactory(state=EncounterState.CANCELLED, medium=EncounterMedium.LAB)
    """

    class Meta:
        model = Encounter

    class Params:
        # State traits
        concluded = factory.Trait(
            state=EncounterState.CONCLUDED,
            end_time=factory.LazyFunction(timezone.now),
        )
        cancelled = factory.Trait(
            state=EncounterState.CANCELLED,
            end_time=None,
        )
        planned = factory.Trait(
            state=EncounterState.PLANNED,
            start_time=None,
            end_time=None,
        )

        # Medium traits
        video = factory.Trait(medium=EncounterMedium.VIDEO)
        voice = factory.Trait(medium=EncounterMedium.VOICE)
        home = factory.Trait(medium=EncounterMedium.HOME)
        lab = factory.Trait(medium=EncounterMedium.LAB)
        offsite = factory.Trait(medium=EncounterMedium.OFFSITE)

    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    medium = EncounterMedium.OFFICE
    state = EncounterState.STARTED
    start_time = factory.LazyFunction(timezone.now)
    end_time = None

import factory

from canvas_sdk.v1.data import Language, Letter, LetterActionEvent
from canvas_sdk.v1.data.letter import EventTypeChoices


class LanguageFactory(factory.django.DjangoModelFactory[Language]):
    """Factory for creating Language."""

    class Meta:
        model = Language

    code = factory.Sequence(lambda n: f"l{n:02d}")
    description = factory.Faker("language_name")


class LetterFactory(factory.django.DjangoModelFactory[Letter]):
    """Factory for creating Letter."""

    class Meta:
        model = Letter

    content = factory.Faker("paragraph")
    printed = None
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")


class LetterActionEventFactory(factory.django.DjangoModelFactory[LetterActionEvent]):
    """Factory for creating LetterActionEvent."""

    class Meta:
        model = LetterActionEvent

    event_type = EventTypeChoices.PRINTED
    send_fax_id = factory.Faker("uuid4")
    received_by_fax = factory.Faker("boolean")
    delivered_by_fax = factory.Faker("boolean")
    fax_result_msg = factory.Faker("paragraph")
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    letter = factory.SubFactory("canvas_sdk.test_utils.factories.LetterFactory")

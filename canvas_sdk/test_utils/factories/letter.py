import factory

from canvas_sdk.v1.data import (
    Language,
    Letter,
    LetterActionEvent,
    LetterLanguageTemplate,
    LetterTemplate,
)
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


class LetterTemplateFactory(factory.django.DjangoModelFactory[LetterTemplate]):
    """Factory for creating LetterTemplate."""

    class Meta:
        model = LetterTemplate

    name = factory.Faker("sentence", nb_words=3)
    active = True
    restrict_editing = False


class LetterLanguageTemplateFactory(factory.django.DjangoModelFactory[LetterLanguageTemplate]):
    """Factory for creating LetterLanguageTemplate."""

    class Meta:
        model = LetterLanguageTemplate

    template = factory.SubFactory("canvas_sdk.test_utils.factories.LetterTemplateFactory")
    language = factory.SubFactory("canvas_sdk.test_utils.factories.LanguageFactory")
    header = ""
    content = factory.Faker("paragraph")
    footer = ""

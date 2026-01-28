import factory

from canvas_sdk.v1.data import Language, Letter


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

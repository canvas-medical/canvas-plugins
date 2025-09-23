import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from canvas_sdk.v1.data.note import (
    Note,
    NoteType,
    NoteTypeCategories,
    NoteTypes,
    PracticeLocationPOS,
)


class NoteTypeFactory(factory.django.DjangoModelFactory[NoteType]):
    """Factory for creating a NoteType."""

    class Meta:
        model = NoteType

    system = FuzzyChoice(["loinc", "internal"])
    version = factory.Faker("slug")
    code = factory.Faker("slug")
    display = factory.Faker("text", max_nb_chars=25)
    user_selected = factory.Faker("boolean", chance_of_getting_true=30)
    name = factory.Faker("text", max_nb_chars=10)
    category = FuzzyChoice(NoteTypeCategories.choices, getter=lambda c: c[0])
    rank = FuzzyInteger(0, 5)
    is_default_appointment_type = factory.Faker("boolean", chance_of_getting_true=10)
    is_scheduleable = factory.Faker("boolean", chance_of_getting_true=70)
    is_telehealth = factory.Faker("boolean", chance_of_getting_true=50)
    is_billable = factory.Faker("boolean", chance_of_getting_true=80)
    defer_place_of_service_to_practice_location = factory.Faker(
        "boolean", chance_of_getting_true=50
    )
    available_places_of_service = FuzzyChoice(PracticeLocationPOS.choices, getter=lambda c: [c[0]])
    default_place_of_service = FuzzyChoice(PracticeLocationPOS.choices, getter=lambda c: c[0])
    is_system_managed = factory.Faker("boolean", chance_of_getting_true=50)
    is_visible = factory.Faker("boolean", chance_of_getting_true=50)
    is_active = factory.Faker("boolean", chance_of_getting_true=50)
    unique_identifier = factory.Faker("uuid")
    is_patient_required = factory.Faker("boolean", chance_of_getting_true=50)
    allow_custom_title = factory.Faker("boolean", chance_of_getting_true=50)
    is_scheduleable_via_patient_portal = factory.Faker("boolean", chance_of_getting_true=50)
    online_duration = FuzzyInteger(0, 5)


class NoteFactory(factory.django.DjangoModelFactory[Note]):
    """Factory for creating a Note."""

    class Meta:
        model = Note

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    # provider = factory.SubFactory(ProviderFactory) # doesn't exist yet
    note_type = FuzzyChoice(NoteTypes.choices, getter=lambda c: c[0])
    note_type_version = factory.SubFactory(NoteTypeFactory)
    title = factory.Faker("sentence", nb_words=4)
    body = factory.Faker("text", max_nb_chars=200)
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.user.CanvasUserFactory")
    checksum = factory.Faker("md5")
    billing_note = factory.Faker("sentence", nb_words=10)
    datetime_of_service = factory.Faker("date_time_between", start_date="-2d", end_date="-1d")
    place_of_service = factory.Faker("text", max_nb_chars=15)

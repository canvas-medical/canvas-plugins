import factory

from canvas_sdk.v1.data.family_history import FamilyHistory, FamilyHistoryCoding


class FamilyHistoryFactory(factory.django.DjangoModelFactory[FamilyHistory]):
    """Factory for creating a FamilyHistory."""

    class Meta:
        model = FamilyHistory

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    relation_snomed_code = factory.Faker("random_int", min=1, max=999999999)
    relation_snomed_term = factory.Faker("word")
    narrative = factory.Faker("text", max_nb_chars=512)


class FamilyHistoryCodingFactory(factory.django.DjangoModelFactory[FamilyHistoryCoding]):
    """Factory for creating a FamilyHistoryCoding."""

    class Meta:
        model = FamilyHistoryCoding

    family_history = factory.SubFactory(FamilyHistoryFactory)
    system = "http://snomed.info/sct"
    code = factory.Faker("numerify", text="######")
    display = factory.Faker("word")
    user_selected = False

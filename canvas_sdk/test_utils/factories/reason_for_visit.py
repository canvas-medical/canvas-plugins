import factory

from canvas_sdk.v1.data import ReasonForVisit, ReasonForVisitCoding


class ReasonForVisitFactory(factory.django.DjangoModelFactory[ReasonForVisit]):
    """Factory for creating a ReasonForVisit."""

    class Meta:
        model = ReasonForVisit

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    legacy_narrative = factory.Faker("paragraph")


class ReasonForVisitCodingFactory(factory.django.DjangoModelFactory[ReasonForVisitCoding]):
    """Factory for creating a ReasonForVisitCoding."""

    class Meta:
        model = ReasonForVisitCoding

    reason_for_visit = factory.SubFactory(ReasonForVisitFactory)
    system = factory.Faker("random_element", elements=["LOINC", "SNOMED", "CPT"])
    code = factory.Faker("bothify", text="#####-#")
    display = factory.Faker("text", max_nb_chars=200)

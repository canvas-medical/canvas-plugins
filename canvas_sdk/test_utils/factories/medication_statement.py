import factory

from canvas_sdk.v1.data import MedicationStatement


class MedicationStatementFactory(factory.django.DjangoModelFactory[MedicationStatement]):
    """Factory for MedicationStatement."""

    class Meta:
        model = MedicationStatement

    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
        originator=factory.SelfAttribute("..originator"),
    )
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    sig_original_input = "1 tab qd po"

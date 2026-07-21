import factory

from canvas_sdk.v1.data import ChangeMedication


class ChangeMedicationFactory(factory.django.DjangoModelFactory[ChangeMedication]):
    """Factory for ChangeMedication."""

    class Meta:
        model = ChangeMedication

    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
        originator=factory.SelfAttribute("..originator"),
    )
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    sig_original_input = "2 tabs qhs po"

import factory

from canvas_sdk.v1.data import EducationalMaterial


class EducationalMaterialFactory(factory.django.DjangoModelFactory[EducationalMaterial]):
    """Factory for EducationalMaterial."""

    class Meta:
        model = EducationalMaterial

    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
        originator=factory.SelfAttribute("..originator"),
    )
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")

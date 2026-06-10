import factory

from canvas_sdk.v1.data import VisualExamFinding


class VisualExamFindingFactory(factory.django.DjangoModelFactory[VisualExamFinding]):
    """Factory for creating VisualExamFinding."""

    class Meta:
        model = VisualExamFinding

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    image = factory.Sequence(lambda n: f"visual_exam_findings/finding_{n}.png")

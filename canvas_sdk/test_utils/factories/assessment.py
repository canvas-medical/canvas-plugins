import factory

from canvas_sdk.v1.data import Assessment
from canvas_sdk.v1.data.assessment import AssessmentStatus


class AssessmentFactory(factory.django.DjangoModelFactory[Assessment]):
    """Factory for creating an Assessment."""

    class Meta:
        model = Assessment

    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    patient = factory.SelfAttribute("note.patient")
    status = AssessmentStatus.STATUS_STABLE
    narrative = ""
    background = ""
    care_team = ""

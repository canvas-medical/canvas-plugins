import factory

from canvas_sdk.v1.data import FollowUp


class FollowUpFactory(factory.django.DjangoModelFactory[FollowUp]):
    """Factory for creating a FollowUp."""

    class Meta:
        model = FollowUp

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    requested_note_type = factory.SubFactory("canvas_sdk.test_utils.factories.NoteTypeFactory")
    reason_for_visit = factory.Faker("sentence")
    requested_appointment_date_original_input = "in 2 weeks"

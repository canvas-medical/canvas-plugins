import factory

from canvas_sdk.v1.data import MedicationStatement


class MedicationStatementFactory(factory.django.DjangoModelFactory):
    """Factory for creating a MedicationStatement."""

    class Meta:
        model = MedicationStatement

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.patient.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.note.NoteFactory")
    medication = factory.SubFactory("canvas_sdk.test_utils.factories.medication.MedicationFactory")
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.user.CanvasUserFactory")
    start_date_original_input = factory.Faker("date_this_century")
    start_date = factory.Faker("date_this_century")
    end_date_original_input = factory.Faker("date_this_century")
    end_date = factory.Faker("date_this_century")
    dose_quantity = factory.Faker("pyfloat", left_digits=2, right_digits=2, positive=True)
    dose_form = factory.Faker("word")
    dose_route = factory.Faker("word")
    dose_frequency = factory.Faker("pyfloat", left_digits=1, right_digits=2, positive=True)
    dose_frequency_interval = factory.Faker("word")
    sig_original_input = factory.Faker("sentence")

    @factory.post_generation
    def indications(self, create: bool, extracted: list | None, **kwargs: object) -> None:
        """Add related Assessment instances to indications M2M field after creation."""
        if not create:
            return
        if extracted:
            for assessment in extracted:
                self.indications.add(assessment)

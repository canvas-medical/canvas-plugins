import factory

from canvas_sdk.v1.data.procedure import Procedure, ProcedureCoding, ProcedureStatus


class ProcedureFactory(factory.django.DjangoModelFactory[Procedure]):
    """Factory for creating a Procedure."""

    class Meta:
        model = Procedure

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    status = ProcedureStatus.COMPLETED
    notes = factory.Faker("sentence")


class ProcedureCodingFactory(factory.django.DjangoModelFactory[ProcedureCoding]):
    """Factory for creating a ProcedureCoding."""

    class Meta:
        model = ProcedureCoding

    procedure = factory.SubFactory(ProcedureFactory)
    system = "http://www.ama-assn.org/go/cpt"
    code = factory.Faker("numerify", text="#####")
    display = factory.Faker("sentence", nb_words=4)
    user_selected = False

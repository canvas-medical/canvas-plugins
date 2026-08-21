import factory

from canvas_sdk.v1.data.vitals import VitalSign, VitalSignReading


class VitalSignReadingFactory(factory.django.DjangoModelFactory[VitalSignReading]):
    """Factory for creating a VitalSignReading."""

    class Meta:
        model = VitalSignReading

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    date_recorded = factory.Faker("date_time")


class VitalSignFactory(factory.django.DjangoModelFactory[VitalSign]):
    """Factory for creating a VitalSign."""

    class Meta:
        model = VitalSign

    reading = factory.SubFactory(VitalSignReadingFactory)
    date_recorded = factory.Faker("date_time")
    loinc_num = "8867-4"
    sign = factory.Sequence(lambda n: f"sign_{n}")
    value = "72"
    units = "bpm"
    source = "Wrist"

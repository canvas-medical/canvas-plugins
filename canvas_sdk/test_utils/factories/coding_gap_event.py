import factory

from canvas_sdk.v1.data import (
    AssessCodingGapEvent,
    CreateCodingGapEvent,
    DeferCodingGapEvent,
    ValidateCodingGapEvent,
)


class CreateCodingGapEventFactory(factory.django.DjangoModelFactory[CreateCodingGapEvent]):
    """Factory for creating a CreateCodingGapEvent."""

    class Meta:
        model = CreateCodingGapEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )


class ValidateCodingGapEventFactory(factory.django.DjangoModelFactory[ValidateCodingGapEvent]):
    """Factory for creating a ValidateCodingGapEvent."""

    class Meta:
        model = ValidateCodingGapEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )


class AssessCodingGapEventFactory(factory.django.DjangoModelFactory[AssessCodingGapEvent]):
    """Factory for creating an AssessCodingGapEvent."""

    class Meta:
        model = AssessCodingGapEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )


class DeferCodingGapEventFactory(factory.django.DjangoModelFactory[DeferCodingGapEvent]):
    """Factory for creating a DeferCodingGapEvent."""

    class Meta:
        model = DeferCodingGapEvent

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )

from typing import TypeVar

import factory

from canvas_sdk.v1.data import (
    AssessCodingGapEvent,
    CreateCodingGapEvent,
    DeferCodingGapEvent,
    ValidateCodingGapEvent,
)

_M = TypeVar("_M")


class CodingGapEventFactory(factory.django.DjangoModelFactory[_M]):
    """Base factory for coding-gap event models."""

    class Meta:
        abstract = True

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )


class CreateCodingGapEventFactory(CodingGapEventFactory[CreateCodingGapEvent]):
    """Factory for creating a CreateCodingGapEvent."""

    class Meta:
        model = CreateCodingGapEvent


class ValidateCodingGapEventFactory(CodingGapEventFactory[ValidateCodingGapEvent]):
    """Factory for creating a ValidateCodingGapEvent."""

    class Meta:
        model = ValidateCodingGapEvent


class AssessCodingGapEventFactory(CodingGapEventFactory[AssessCodingGapEvent]):
    """Factory for creating an AssessCodingGapEvent."""

    class Meta:
        model = AssessCodingGapEvent


class DeferCodingGapEventFactory(CodingGapEventFactory[DeferCodingGapEvent]):
    """Factory for creating a DeferCodingGapEvent."""

    class Meta:
        model = DeferCodingGapEvent

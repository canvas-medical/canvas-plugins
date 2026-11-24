import factory

from canvas_sdk.v1.data import (
    DiagnosticView,
    DiagnosticViewElement,
    DiagnosticViewElementCodingSystem,
    DiagnosticViewElementDataType,
)


class DiagnosticViewFactory(factory.django.DjangoModelFactory[DiagnosticView]):
    """Factory for creating a DiagnosticView."""

    class Meta:
        model = DiagnosticView

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    name = factory.Faker("sentence", nb_words=2)


class DiagnosticViewElementFactory(factory.django.DjangoModelFactory[DiagnosticViewElement]):
    """Factory for creating a DiagnosticViewElement."""

    class Meta:
        model = DiagnosticViewElement

    view = factory.SubFactory(DiagnosticViewFactory)
    data_type = DiagnosticViewElementDataType.LAB_VALUE
    system = DiagnosticViewElementCodingSystem.LOINC
    code = "4548-4"
    name = "Hemoglobin A1c"
    units = "%"
    ordering = factory.Sequence(lambda n: n)

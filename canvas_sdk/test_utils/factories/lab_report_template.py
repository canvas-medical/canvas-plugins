import factory

from canvas_sdk.v1.data import (
    LabReportTemplate,
    LabReportTemplateField,
    LabReportTemplateFieldOption,
)
from canvas_sdk.v1.data.lab import FieldType


class LabReportTemplateFactory(factory.django.DjangoModelFactory[LabReportTemplate]):
    """Factory for creating a LabReportTemplate."""

    class Meta:
        model = LabReportTemplate

    name = factory.Faker("sentence", nb_words=3)
    code = factory.Faker("bothify", text="????-####")
    code_system = "http://loinc.org"
    search_keywords = factory.Faker("sentence", nb_words=5)
    active = True
    custom = True
    poc = False


class LabReportTemplateFieldFactory(factory.django.DjangoModelFactory[LabReportTemplateField]):
    """Factory for creating a LabReportTemplateField."""

    class Meta:
        model = LabReportTemplateField

    report_template = factory.SubFactory(LabReportTemplateFactory)
    sequence = factory.Sequence(lambda n: n + 1)
    code = factory.Faker("bothify", text="####-#")
    code_system = "http://loinc.org"
    label = factory.Faker("sentence", nb_words=2)
    units = factory.Faker("random_element", elements=["mg/dL", "g/L", "%", "mmol/L", None])
    type = FieldType.FLOAT
    required = False


class LabReportTemplateFieldOptionFactory(
    factory.django.DjangoModelFactory[LabReportTemplateFieldOption]
):
    """Factory for creating a LabReportTemplateFieldOption."""

    class Meta:
        model = LabReportTemplateFieldOption

    field = factory.SubFactory(LabReportTemplateFieldFactory)
    label = factory.Faker("word")
    key = factory.Faker("slug")

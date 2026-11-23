import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import ConsolidatedImmunization, ConsolidatedImmunizationCoding


class ConsolidatedImmunizationFactory(factory.django.DjangoModelFactory[ConsolidatedImmunization]):
    """Factory for creating a ConsolidatedImmunization."""

    class Meta:
        model = ConsolidatedImmunization

    content_type = factory.SubFactory(ContentTypeFactory, model="immunization")
    object_id = factory.Sequence(lambda n: n + 1)
    primary_source = True
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory", patient=factory.SelfAttribute("..patient")
    )
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")


class ConsolidatedImmunizationCodingFactory(
    factory.django.DjangoModelFactory[ConsolidatedImmunizationCoding]
):
    """Factory for creating a ConsolidatedImmunizationCoding."""

    class Meta:
        model = ConsolidatedImmunizationCoding

    consolidated_immunization = factory.SubFactory(ConsolidatedImmunizationFactory)
    content_type = factory.SubFactory(ContentTypeFactory, model="immunizationcoding")
    object_id = factory.Sequence(lambda n: n + 1)
    system = "http://hl7.org/fhir/sid/cvx"
    code = "208"
    display = "SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 30 mcg/0.3mL dose"

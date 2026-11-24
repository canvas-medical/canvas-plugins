import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import LetterDocument, PatientChartDocument, ReferralDocument


class PatientChartDocumentFactory(factory.django.DjangoModelFactory[PatientChartDocument]):
    """Factory for creating PatientChartDocument."""

    class Meta:
        model = PatientChartDocument

    name = factory.Sequence(lambda n: f"Chart page {n}")
    url = "api/Patient/{key}.html?&usage=chart_summary&audience=care_team"


class LetterDocumentFactory(factory.django.DjangoModelFactory[LetterDocument]):
    """Factory for creating LetterDocument."""

    class Meta:
        model = LetterDocument

    letter = factory.SubFactory("canvas_sdk.test_utils.factories.LetterFactory")
    label = factory.Faker("sentence", nb_words=3)
    content_type = factory.SubFactory(ContentTypeFactory, model="uncategorizedclinicaldocument")
    object_id = factory.Sequence(lambda n: n + 1)


class ReferralDocumentFactory(factory.django.DjangoModelFactory[ReferralDocument]):
    """Factory for creating ReferralDocument."""

    class Meta:
        model = ReferralDocument

    referral = factory.SubFactory("canvas_sdk.test_utils.factories.ReferralFactory")
    document_type = "LAB REPORT"
    label = factory.Faker("sentence", nb_words=3)
    document_id = factory.Sequence(lambda n: n + 1)

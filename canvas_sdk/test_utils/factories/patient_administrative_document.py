import datetime

import factory
from factory.fuzzy import FuzzyDate

from canvas_sdk.v1.data import DocumentCoding, PatientAdministrativeDocument


class DocumentCodingFactory(factory.django.DjangoModelFactory[DocumentCoding]):
    """Factory for DocumentCoding."""

    class Meta:
        model = DocumentCoding

    system = "http://loinc.org"
    code = "34133-9"
    display = "Summary of episode note"
    user_selected = False


class PatientAdministrativeDocumentFactory(
    factory.django.DjangoModelFactory[PatientAdministrativeDocument]
):
    """Factory for PatientAdministrativeDocument."""

    class Meta:
        model = PatientAdministrativeDocument

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    name = factory.Faker("sentence", nb_words=3)
    review_mode = factory.Faker("random_element", elements=["IN", "OT"])
    comment = factory.Faker("paragraph")
    document = "administrative/doc.pdf"
    original_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365),
        end_date=datetime.date.today(),
    )

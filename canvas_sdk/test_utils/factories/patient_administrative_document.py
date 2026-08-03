import datetime

import factory
from factory.fuzzy import FuzzyDate

from canvas_sdk.v1.data import PatientAdministrativeDocument


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

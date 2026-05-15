import datetime

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyDate

from canvas_sdk.v1.data import UncategorizedClinicalDocument, UncategorizedClinicalDocumentReview


class UncategorizedClinicalDocumentReviewFactory(
    factory.django.DjangoModelFactory[UncategorizedClinicalDocumentReview]
):
    """Factory for creating UncategorizedClinicalDocumentReview."""

    class Meta:
        model = UncategorizedClinicalDocumentReview

    internal_comment = factory.Faker("paragraph")
    message_to_patient = factory.Faker("sentence", nb_words=20)
    status = factory.Faker("random_element", elements=["pending", "reviewed", "completed"])
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    patient_communication_method = factory.Faker(
        "random_element", elements=["email", "phone", "portal", "mail"]
    )


class UncategorizedClinicalDocumentFactory(
    factory.django.DjangoModelFactory[UncategorizedClinicalDocument]
):
    """Factory for creating UncategorizedClinicalDocument."""

    class Meta:
        model = UncategorizedClinicalDocument

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    review = factory.SubFactory(UncategorizedClinicalDocumentReviewFactory)
    assigned_by = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")

    name = factory.Faker("sentence", nb_words=3)
    review_mode = factory.Faker("random_element", elements=["IN", "OT"])
    requires_signature = factory.Faker("boolean")
    assigned_date = factory.LazyFunction(lambda: timezone.now())
    original_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365),
        end_date=datetime.date.today(),
    )
    comment = factory.Faker("paragraph")

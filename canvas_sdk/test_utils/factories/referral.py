import datetime
import json
from typing import Any

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyDate

from canvas_sdk.v1.data import Referral, ReferralReport, ReferralReview


class ReferralFactory(factory.django.DjangoModelFactory[Referral]):
    """Factory for creating a Referral."""

    class Meta:
        model = Referral

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    service_provider = None  # Optional field
    clinical_question = factory.Faker("text", max_nb_chars=50)
    priority = factory.Faker("random_element", elements=["routine", "urgent", "stat"])
    include_visit_note = False
    notes = factory.Faker("paragraph")
    date_referred = factory.LazyFunction(lambda: timezone.now())
    forwarded = False
    internal_comment = factory.Faker("paragraph")
    internal_task_comment = None  # Optional field
    ignored = False
    task_ids = factory.LazyFunction(lambda: json.dumps([]))

    @factory.post_generation
    def assessments(self, create: Any, extracted: Any, **kwargs: Any) -> None:
        """Handle many-to-many relationship for assessments."""
        if not create:
            return

        if extracted:
            for assessment in extracted:
                self.assessments.add(assessment)


class ReferralReviewFactory(factory.django.DjangoModelFactory[ReferralReview]):
    """Factory for creating a ReferralReview."""

    class Meta:
        model = ReferralReview

    internal_comment = factory.Faker("paragraph")
    message_to_patient = factory.Faker("sentence", nb_words=20)
    status = factory.Faker("random_element", elements=["pending", "reviewed", "completed"])
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    patient_communication_method = factory.Faker(
        "random_element", elements=["email", "phone", "portal", "mail"]
    )


class ReferralReportFactory(factory.django.DjangoModelFactory[ReferralReport]):
    """Factory for creating a ReferralReport."""

    class Meta:
        model = ReferralReport

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    review_mode = factory.Faker("random_element", elements=["IN", "OT"])
    assigned_by = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    junked = False
    requires_signature = factory.Faker("boolean")
    assigned_date = factory.LazyFunction(lambda: timezone.now())
    team_assigned_date = None
    team = None
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    referral = factory.SubFactory(ReferralFactory)
    specialty = factory.Faker("job")
    review = None
    original_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365),
        end_date=datetime.date.today(),
    )
    comment = factory.Faker("paragraph")
    priority = False

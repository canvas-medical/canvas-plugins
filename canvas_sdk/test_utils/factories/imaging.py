import datetime
import json

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyDate

from canvas_sdk.v1.data import ImagingOrder, ImagingReport, ImagingReview
from canvas_sdk.v1.data.common import (
    DocumentReviewMode,
    OrderStatus,
    ReviewPatientCommunicationMethod,
    ReviewStatus,
)
from canvas_sdk.v1.data.imaging import ImagingReport as ImagingReportModel


class ImagingOrderFactory(factory.django.DjangoModelFactory[ImagingOrder]):
    """Factory for creating an ImagingOrder."""

    class Meta:
        model = ImagingOrder

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    imaging = factory.Faker("text", max_nb_chars=1024)
    imaging_center = None  # Optional field
    note_to_radiologist = factory.Faker("text", max_nb_chars=1024)
    internal_comment = factory.Faker("text", max_nb_chars=1024)
    status = OrderStatus.REQUESTED
    date_time_ordered = factory.LazyFunction(lambda: timezone.now())
    priority = factory.Faker("random_element", elements=["routine", "urgent", "stat"])
    ordering_provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    delegated = False
    task_ids = factory.LazyFunction(lambda: json.dumps([]))


class ImagingReviewFactory(factory.django.DjangoModelFactory[ImagingReview]):
    """Factory for creating an ImagingReview."""

    class Meta:
        model = ImagingReview

    patient_communication_method = ReviewPatientCommunicationMethod.DELEGATED_CALL_CAN_LEAVE_MESSAGE
    internal_comment = factory.Faker("text", max_nb_chars=2048)
    message_to_patient = factory.Faker("text", max_nb_chars=2048)
    is_released_to_patient = False
    status = ReviewStatus.STATUS_REVIEWING
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")


class ImagingReportFactory(factory.django.DjangoModelFactory[ImagingReport]):
    """Factory for creating an ImagingReport."""

    class Meta:
        model = ImagingReport

    review_mode = DocumentReviewMode.REVIEW_REQUIRED
    junked = False
    requires_signature = False
    assigned_date = factory.LazyFunction(lambda: timezone.now())
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    order = None  # Optional field
    source = ImagingReportModel.ImagingReportSource.DIRECTLY_REPORT
    name = factory.Faker("text", max_nb_chars=255)
    result_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365),
        end_date=datetime.date.today(),
    )
    original_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365),
        end_date=datetime.date.today(),
    )
    review = None  # Optional field

import factory
from django.utils import timezone

from canvas_sdk.v1.data import DetectedIssue, DetectedIssueMitigation


class DetectedIssueFactory(factory.django.DjangoModelFactory[DetectedIssue]):
    """Factory for creating a DetectedIssue."""

    class Meta:
        model = DetectedIssue

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    identified = factory.LazyFunction(timezone.now)
    code = "CODINGGAP"
    status = DetectedIssue.Status.REGISTERED
    reference = ""
    issue_identifier = ""
    issue_identifier_system = ""
    detail = ""


class DetectedIssueMitigationFactory(factory.django.DjangoModelFactory[DetectedIssueMitigation]):
    """Factory for creating a DetectedIssueMitigation."""

    class Meta:
        model = DetectedIssueMitigation

    detected_issue = factory.SubFactory(DetectedIssueFactory)
    author = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    action = DetectedIssueMitigation.Action.VALID
    date = factory.LazyFunction(timezone.now)

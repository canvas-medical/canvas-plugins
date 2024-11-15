from django.db import models


class DocumentReviewMode(models.TextChoices):
    """Choices for document reviews."""

    REVIEW_REQUIRED = "RR", "Review required"
    ALREADY_REVIEWED_OFFLINE = "AR", "Already reviewed offline"
    REVIEW_NOT_REQUIRED = "RN", "Review not required"


class OrderStatus(models.TextChoices):
    """Choices for Order statuses."""

    PROPOSED = "proposed", "Proposed"
    DRAFT = "draft", "Draft"
    PLANNED = "planned", "Planned"
    REQUESTED = "requested", "Requested"
    RECEIVED = "received", "Received"
    ACCEPTED = "accepted", "Accepted"
    IN_PROGRESS = "in-progress", "In-progress"
    REVIEW = "review", "Review"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    SUSPENDED = "suspended", "Suspended"
    REJECTED = "rejected", "Rejected"
    FAILED = "failed", "Failed"
    ENTERED_IN_ERROR = "EIE", "Entered in Error"


class ReviewPatientCommunicationMethod(models.TextChoices):
    """Choices for patient communication regarding reviews."""

    DELEGATED_CALL_CAN_LEAVE_MESSAGE = "DM", "delegate call, can leave message"
    DELEGATED_CALL_NEED_ANSWER = "DA", "delegate call, need patient to answer"
    DELEGATED_LETTER = "DL", "delegate letter"
    DO_NOT_COMMUNICATE = "DC", "do not communicate"
    ALREADY_LEFT_MESSAGE = "AM", "already left message"
    ALREADY_REVIEWED_WITH_PATIENT = "AR", "already reviewed with patient"


class ReviewStatus(models.TextChoices):
    """Status choices for reviews."""

    STATUS_REVIEWING = "reviewing", "reviewing"
    STATUS_REVIEWED = "reviewed", "reviewed"

class DocumentReviewMode:
    REVIEW_REQUIRED = "RR"
    ALREADY_REVIEWED_OFFLINE = "AR"
    REVIEW_NOT_REQUIRED = "RN"

    CHOICES = {
        REVIEW_REQUIRED: "Review required",
        ALREADY_REVIEWED_OFFLINE: "Already reviewed offline",
        REVIEW_NOT_REQUIRED: "Review not required",
    }


class OrderStatus:
    PROPOSED = "proposed"
    DRAFT = "draft"
    PLANNED = "planned"
    REQUESTED = "requested"
    RECEIVED = "received"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in-progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    FAILED = "failed"
    ENTERED_IN_ERROR = "EIE"

    CHOICES = {
        PROPOSED: "Proposed",
        DRAFT: "Draft",
        PLANNED: "Planned",
        REQUESTED: "Requested",
        RECEIVED: "Received",
        ACCEPTED: "Accepted",
        IN_PROGRESS: "In-progress",
        REVIEW: "Review",
        COMPLETED: "Completed",
        CANCELLED: "Cancelled",
        SUSPENDED: "Suspended",
        REJECTED: "Rejected",
        FAILED: "Failed",
        ENTERED_IN_ERROR: "Entered in Error",
    }


class ReviewPatientCommunicationMethod:
    DELEGATED_CALL_CAN_LEAVE_MESSAGE = "DM"
    DELEGATED_CALL_NEED_ANSWER = "DA"
    DELEGATED_LETTER = "DL"
    DO_NOT_COMMUNICATE = "DC"
    ALREADY_LEFT_MESSAGE = "AM"
    ALREADY_REVIEWED_WITH_PATIENT = "AR"

    CHOICES = {
        DELEGATED_CALL_CAN_LEAVE_MESSAGE: "delegate call, can leave message",
        DELEGATED_CALL_NEED_ANSWER: "delegate call, need patient to answer",
        DELEGATED_LETTER: "delegate letter",
        DO_NOT_COMMUNICATE: "do not communicate",
        ALREADY_LEFT_MESSAGE: "already left message",
        ALREADY_REVIEWED_WITH_PATIENT: "already reviewed with patient",
    }


class ReviewStatus:
    STATUS_REVIEWING = "reviewing"
    STATUS_REVIEWED = "reviewed"

    CHOICES = {
        STATUS_REVIEWING: "reviewing",
        STATUS_REVIEWING: "reviewed",
    }

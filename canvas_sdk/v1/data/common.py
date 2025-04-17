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


class PersonSex(models.TextChoices):
    """Status choices for individual sex."""

    SEX_FEMALE = "F", "female"
    SEX_MALE = "M", "male"
    SEX_OTHER = "O", "other"
    SEX_UNKNOWN = "UNK", "unknown"
    SEX_BLANK = "", ""


class TaxIDType(models.TextChoices):
    """Choices for Tax IDs."""

    EIN = "E", "EIN text"
    SSN = "S", "SSN"


class ColorEnum(models.TextChoices):
    """Choices for colors."""

    RED = "red", "Red"
    ORANGE = "orange", "Orange"
    YELLOW = "yellow", "Yellow"
    OLIVE = "olive", "Olive"
    GREEN = "green", "Green"
    TEAL = "teal", "Teal"
    BLUE = "blue", "Blue"
    VIOLET = "violet", "Violet"
    PURPLE = "purple", "Purple"
    PINK = "pink", "Pink"
    BROWN = "brown", "Brown"
    GREY = "grey", "Grey"
    BLACK = "black", "Black"


class Origin(models.TextChoices):
    """Choices for origins."""

    REFERAL = ("REF_CMD", "Referral command")
    COMPLETING_IMAGE_ORDERS = ("CMP_IMG_ORD", "Completing image orders")
    IMAGING_REPORT_REVIEW = ("IMG_REP_REV", "Imaging report review")
    LAB_RESULTS_REVIEW = ("LAB_RES_REV", "Lab results review")
    CONSULT_REPORT_REVIEW = ("CON_REP_REV", "Consult report review")
    UNCATEGORIZED_DOCUMENT_REPORT_REVIEW = (
        "UNC_DOC_REP_REV",
        "Uncategorized document report review",
    )
    ASSIGNED_NOTE_PHONE_CALL_FOR_REVIEW = ("ASN_NOT_PHN_REV", "Assigned note/phone call for review")
    POPULATION_HEALTH_OUTREACH = ("POP_HLT_OUT", "Population health outreach")
    COMPLETING_LAB_ORDERS = ("CMP_LAB_ORD", "Completing lab orders")
    CHART_PDF = ("CHT_PDF", "Chart PDF")
    EXPIRED_CLAIM_SNOOZED = ("EXP_CLM_SNO", "Expired claim snoozed")
    FLAGGED_POSTING_REVIEW = ("FLG_PST_REV", "Flagged posting review")
    BATCH_PATIENT_STATEMENTS = ("BAT_PTN_STA", "Batch patient statements")
    INCOMPLETE_COVERAGE = ("INC_COV", "Incomplete Coverage")


class ContactPointSystem(models.TextChoices):
    """ContactPointSystem."""

    PHONE = "phone", "phone"
    FAX = "fax", "fax"
    EMAIL = "email", "email"
    PAGER = "pager", "pager"
    OTHER = "other", "other"


class ContactPointUse(models.TextChoices):
    """ContactPointUse."""

    HOME = "home", "Home"
    WORK = "work", "Work"
    TEMP = "temp", "Temp"
    OLD = "old", "Old"
    OTHER = "other", "Other"
    MOBILE = "mobile", "Mobile"
    AUTOMATION = "automation", "Automation"


class ContactPointState(models.TextChoices):
    """ContactPointState."""

    ACTIVE = "active", "Active"
    DELETED = "deleted", "Deleted"


class AddressUse(models.TextChoices):
    """AddressUse."""

    HOME = "home", "Home"
    WORK = "work", "Work"
    TEMP = "temp", "Temp"
    OLD = "old", "Old"


class AddressType(models.TextChoices):
    """AddressType."""

    POSTAL = "postal", "Postal"
    PHYSICAL = "physical", "Physical"
    BOTH = "both", "Both"


class AddressState(models.TextChoices):
    """AddressState."""

    ACTIVE = "active", "Active"
    DELETED = "deleted", "Deleted"


__exports__ = (
    "DocumentReviewMode",
    "OrderStatus",
    "ReviewPatientCommunicationMethod",
    "ReviewStatus",
    "PersonSex",
    "TaxIDType",
    "ColorEnum",
    "Origin",
    "ContactPointSystem",
    "ContactPointUse",
    "ContactPointState",
    "AddressUse",
    "AddressType",
    "AddressState",
)

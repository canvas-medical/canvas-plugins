from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
    TimeframeLookupQuerySetMixin,
    ValueSetLookupQuerySet,
)
from canvas_sdk.v1.data.staff import Staff


class LabReportQuerySet(BaseQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin):
    """A queryset for lab reports."""

    pass


LabReportManager = BaseModelManager.from_queryset(LabReportQuerySet)


class TransmissionType(models.TextChoices):
    """Choices for transmission types."""

    FAX = "F", "fax"
    HL7 = "H", "hl7"
    MANUAL = "M", "manual"


class LabReport(IdentifiableModel):
    """A class representing a lab report."""

    class Meta:
        db_table = "canvas_sdk_data_api_labreport_001"

    objects = cast(LabReportQuerySet, LabReportManager())

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    review_mode = models.CharField(max_length=2)
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="lab_reports", null=True
    )
    transmission_type = models.CharField(choices=TransmissionType.choices, max_length=10)
    for_test_only = models.BooleanField()
    external_id = models.CharField(max_length=40)
    version = models.IntegerField()
    requisition_number = models.CharField(max_length=40)
    review = models.ForeignKey(
        "LabReview", on_delete=models.DO_NOTHING, related_name="reports", null=True
    )
    original_date = models.DateTimeField()
    date_performed = models.DateTimeField()
    custom_document_name = models.CharField(max_length=500)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()


class LabReviewQuerySet(BaseQuerySet, CommittableQuerySetMixin, ForPatientQuerySetMixin):
    """A queryset for lab reviews."""

    pass


LabReviewManager = BaseModelManager.from_queryset(LabReviewQuerySet)


class LabReview(IdentifiableModel):
    """A class representing a lab review."""

    class Meta:
        db_table = "canvas_sdk_data_api_labreview_001"

    objects = cast(LabReviewQuerySet, LabReviewManager())

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    internal_comment = models.TextField()
    message_to_patient = models.CharField(max_length=2048)
    status = models.CharField(max_length=50)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="lab_reviews", null=True
    )
    patient_communication_method = models.CharField(max_length=30)


class LabValueTimeframeLookupQuerySetMixin(TimeframeLookupQuerySetMixin):
    """A class that adds queryset functionality to filter using timeframes."""

    @property
    def timeframe_filter_field(self) -> str:
        """Returns the field that should be filtered on. Can be overridden for different models."""
        return "report__original_date"


class LabValueQuerySet(ValueSetLookupQuerySet, LabValueTimeframeLookupQuerySetMixin):
    """LabValueQuerySet."""

    pass


class LabValue(IdentifiableModel):
    """A class representing a lab value."""

    class Meta:
        db_table = "canvas_sdk_data_api_labvalue_001"

    objects = LabValueQuerySet.as_manager()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    report = models.ForeignKey(
        "LabReport", on_delete=models.DO_NOTHING, related_name="values", null=True
    )
    value = models.TextField()
    units = models.CharField(max_length=30)
    abnormal_flag = models.CharField(max_length=128)
    reference_range = models.CharField(max_length=128)
    low_threshold = models.CharField(max_length=30)
    high_threshold = models.CharField(max_length=30)
    comment = models.TextField()
    observation_status = models.CharField(max_length=24)


class LabValueCoding(Model):
    """A class representing a lab value coding."""

    class Meta:
        db_table = "canvas_sdk_data_api_labvaluecoding_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    value = models.ForeignKey(
        LabValue, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )
    code = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    system = models.CharField(max_length=128)


class LabOrder(IdentifiableModel):
    """A class representing a lab order."""

    class SpecimenCollectionType(models.TextChoices):
        """Choices for specimen collection types."""

        ON_LOCATION = "L", "on location"
        PATIENT_SERVICE_CENTER = "P", "patient service center"
        OTHER = "O", "other"

    class CourtesyCopyType(models.TextChoices):
        """Choices for courtesy copy types."""

        ACCOUNT = "A", "account"
        FAX = "F", "fax"
        PATIENT = "P", "patient"

    class ManualProcessingStatus(models.TextChoices):
        """Choices for manual processing statuses."""

        MANUAL_PROCESSING_STATUS_NEEDS_REVIEW = "NEEDS_REVIEW", "Needs Review"
        MANUAL_PROCESSING_STATUS_IN_PROGRESS = "IN_PROGRESS", "In Progress"
        MANUAL_PROCESSING_STATUS_PROCESSED = "PROCESSED", "Processed"
        MANUAL_PROCESSING_STATUS_FLAGGED = "FLAGGED", "Flagged"

    class Meta:
        db_table = "canvas_sdk_data_api_laborder_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="lab_orders", null=True
    )
    ontology_lab_partner = models.CharField(max_length=128)

    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, null=True)
    comment = models.CharField(max_length=128)
    requisition_number = models.CharField(max_length=32)
    is_patient_bill = models.BooleanField(null=True)
    date_ordered = models.DateTimeField()
    fasting_status = models.BooleanField(null=True)
    specimen_collection_type = models.CharField(
        choices=SpecimenCollectionType.choices, null=True, max_length=10
    )
    transmission_type = models.CharField(choices=TransmissionType.choices, null=True, max_length=10)
    courtesy_copy_type = models.CharField(
        choices=CourtesyCopyType.choices, null=True, max_length=10
    )
    courtesy_copy_number = models.CharField(max_length=32)
    courtesy_copy_text = models.CharField(max_length=64)
    ordering_provider = models.ForeignKey(
        Staff, on_delete=models.DO_NOTHING, related_name="lab_orders", null=True
    )
    parent_order = models.ForeignKey("v1.LabOrder", on_delete=models.DO_NOTHING, null=True)
    healthgorilla_id = models.CharField(max_length=40)
    manual_processing_status = models.CharField(
        choices=ManualProcessingStatus.choices, null=True, max_length=16
    )
    manual_processing_comment = models.TextField(null=True)
    labcorp_abn_url = models.URLField()

    reports = models.ManyToManyField("v1.LabReport", through="v1.LabTest")


class LabOrderReason(Model):
    """A class representing a lab order reason."""

    class LabReasonMode(models.TextChoices):
        """Choices for lab order reasons."""

        MONITOR = "MO", "monitor"
        INVESTIGATE = "IN", "investigate"
        SCREEN_FOR = "SF", "screen for"
        UNKNOWN = "UNK", "unknown"

    class Meta:
        db_table = "canvas_sdk_data_api_laborderreason_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    order = models.ForeignKey(
        LabOrder, on_delete=models.DO_NOTHING, related_name="reasons", null=True
    )
    mode = models.CharField(max_length=30, choices=LabReasonMode)


class LabOrderReasonCondition(Model):
    """A class representing a lab order reason's condition."""

    class Meta:
        db_table = "canvas_sdk_data_api_laborderreasoncondition_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    reason = models.ForeignKey(
        LabOrderReason, on_delete=models.DO_NOTHING, related_name="reason_conditions", null=True
    )
    condition = models.ForeignKey(
        "v1.Condition",
        on_delete=models.DO_NOTHING,
        related_name="lab_order_reason_conditions",
        null=True,
    )


class LabTest(IdentifiableModel):
    """A class representing a lab test."""

    class LabTestOrderStatus(models.TextChoices):
        """Choicees for lab test order statuses."""

        NEW = "NE", "new"
        STAGED_FOR_REQUISITION = "SR", "staged for requisition"
        SENDING = "SE", "sending"
        SENDING_FAILED = "SF", "sending failed"
        PROCESSING = "PR", "processing"
        PROCESSING_FAILED = "PF", "processing failed"
        RECEIVED = "RE", "received"
        REVIEWED = "RV", "reviewed"
        INACTIVE = "IN", "inactive"

    class Meta:
        db_table = "canvas_sdk_data_api_labtest_001"

    ontology_test_name = models.CharField(max_length=512, blank=True, default="")
    ontology_test_code = models.CharField(max_length=512, blank=True, default="")
    status = models.CharField(max_length=30, choices=LabTestOrderStatus.choices)
    report = models.ForeignKey(
        LabReport, on_delete=models.DO_NOTHING, related_name="tests", null=True
    )
    aoe_code = models.CharField(max_length=10, default="")
    procedure_class = models.CharField(max_length=10, default="")
    specimen_type = models.CharField(max_length=26)
    specimen_source_code = models.CharField(max_length=5)
    specimen_source_description = models.CharField(max_length=255)
    specimen_source_coding_system = models.CharField(max_length=5)
    order = models.ForeignKey(
        LabOrder, on_delete=models.DO_NOTHING, related_name="tests", null=True
    )

    def __str__(self) -> str:
        return f"{self.ontology_test_name}: f{self.ontology_test_code}"


class LabPartner(IdentifiableModel):
    """A class representing a lab partner."""

    class Meta:
        db_table = "canvas_sdk_data_lab_partner_001"

    objects: models.Manager["LabPartner"]

    name = models.CharField(max_length=256)
    active = models.BooleanField()
    electronic_ordering_enabled = models.BooleanField()
    keywords = models.TextField()
    default_lab_account_number = models.CharField(max_length=256)


class LabPartnerTest(IdentifiableModel):
    """A class representing a lab partner's test."""

    class Meta:
        db_table = "canvas_sdk_data_lab_partner_test_001"

    objects: models.Manager["LabPartnerTest"]

    lab_partner = models.ForeignKey(
        "LabPartner", on_delete=models.DO_NOTHING, related_name="available_tests"
    )
    order_code = models.CharField(max_length=256, blank=True)
    order_name = models.TextField()
    keywords = models.TextField(blank=True)
    cpt_code = models.CharField(max_length=256, blank=True, null=True)


__exports__ = (
    "TransmissionType",
    "LabReport",
    "LabReviewQuerySet",
    "LabReview",
    "LabValue",
    "LabValueCoding",
    "LabOrder",
    "LabOrderReason",
    "LabOrderReasonCondition",
    "LabTest",
    "LabPartner",
    "LabPartnerTest",
)

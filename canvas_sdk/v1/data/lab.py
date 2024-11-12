from django.db import models

from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.patient import Patient

# from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.user import CanvasUser


class TransmissionType(models.TextChoices):
    """Choices for transmission types."""

    FAX = "F", "fax"
    HL7 = "H", "hl7"
    MANUAL = "M", "manual"


class LabReport(models.Model):
    """A class representing a lab report."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labreport_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    review_mode = models.CharField()
    junked = models.BooleanField()
    requires_signature = models.BooleanField()
    assigned_date = models.DateTimeField()
    patient = models.ForeignKey(
        Patient, on_delete=models.DO_NOTHING, related_name="lab_reports", null=True
    )
    transmission_type = models.CharField(choices=TransmissionType)
    for_test_only = models.BooleanField()
    external_id = models.CharField()
    version = models.IntegerField()
    requisition_number = models.CharField()
    review = models.ForeignKey(
        "LabReview", related_name="reports", on_delete=models.DO_NOTHING, null=True
    )
    original_date = models.DateTimeField()
    date_performed = models.DateTimeField()
    custom_document_name = models.CharField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()


class LabReview(models.Model):
    """A class representing a lab review."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labreview_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    internal_comment = models.TextField()
    message_to_patient = models.CharField()
    status = models.CharField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="lab_reviews")
    patient_communication_method = models.CharField()


class LabValue(models.Model):
    """A class representing a lab value."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labvalue_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    report = models.ForeignKey(
        "LabReport", related_name="values", on_delete=models.DO_NOTHING, null=True
    )
    value = models.TextField()
    units = models.CharField()
    abnormal_flag = models.CharField()
    reference_range = models.CharField()
    low_threshold = models.CharField()
    high_threshold = models.CharField()
    comment = models.TextField()
    observation_status = models.CharField()


class LabValueCoding(models.Model):
    """A class representing a lab value coding."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labvaluecoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    value = models.ForeignKey(
        LabValue, on_delete=models.DO_NOTHING, related_name="codings", null=True
    )
    code = models.CharField()
    name = models.CharField()
    system = models.CharField()


class LabOrder(models.Model):
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
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_laborder_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, related_name="lab_orders")
    ontology_lab_partner = models.CharField()
    # TODO - uncomment when the Note model is finished
    # note = models.ForeignKey("Note", on_delete=models.DO_NOTHING)
    comment = models.CharField()
    requisition_number = models.CharField()
    is_patient_bill = models.BooleanField(null=True)
    date_ordered = models.DateTimeField()
    fasting_status = models.BooleanField(null=True)
    specimen_collection_type = models.CharField(choices=SpecimenCollectionType, null=True)
    transmission_type = models.CharField(choices=TransmissionType, null=True)
    courtesy_copy_type = models.CharField(choices=CourtesyCopyType, null=True)
    courtesy_copy_number = models.CharField()
    courtesy_copy_text = models.CharField()
    # TODO - uncomment when Staff model is added
    # ordering_provider = models.ForeignKey(Staff, on_delete=models.DO_NOTHING, null=True)
    parent_order = models.ForeignKey("LabOrder", on_delete=models.DO_NOTHING, null=True)
    healthgorilla_id = models.CharField()
    manual_processing_status = models.CharField(choices=ManualProcessingStatus)
    manual_processing_comment = models.CharField()
    labcorp_abn_url = models.URLField()


class LabOrderReason(models.Model):
    """A class representing a lab order reason."""

    class LabReasonMode(models.TextChoices):
        """Choices for lab order reasons."""

        MONITOR = "MO", "monitor"
        INVESTIGATE = "IN", "investigate"
        SCREEN_FOR = "SF", "screen for"
        UNKNOWN = "UNK", "unknown"

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_laborderreason_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(LabOrder, on_delete=models.DO_NOTHING, related_name="reasons")
    mode = models.CharField(max_length=30, choices=LabReasonMode)


class LabOrderReasonCondition(models.Model):
    """A class representing a lab order reason's condition."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_laborderreasoncondition_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    reason = models.ForeignKey(
        LabOrderReason, on_delete=models.DO_NOTHING, related_name="reason_conditions", null=True
    )
    condition = models.ForeignKey(
        Condition,
        on_delete=models.DO_NOTHING,
        related_name="lab_order_reason_conditions",
        null=True,
    )


class LabTest(models.Model):
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
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_labtest_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    ontology_test_name = models.CharField(max_length=512, blank=True, default="")
    ontology_test_code = models.CharField(max_length=512, blank=True, default="")
    status = models.CharField(max_length=30, choices=LabTestOrderStatus)
    report = models.ForeignKey(
        LabReport, on_delete=models.DO_NOTHING, null=True, related_name="tests"
    )
    aoe_code = models.CharField(max_length=10, default="")
    procedure_class = models.CharField(max_length=10, default="")
    specimen_type = models.CharField()
    specimen_source_code = models.CharField()
    specimen_source_description = models.CharField()
    specimen_source_coding_system = models.CharField()
    order = models.ForeignKey(
        LabOrder, on_delete=models.DO_NOTHING, related_name="tests", null=True
    )

    def __str__(self) -> str:
        return f"{self.ontology_test_name}: f{self.ontology_test_code}"

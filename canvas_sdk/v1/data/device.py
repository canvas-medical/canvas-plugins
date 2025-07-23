from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class Device(IdentifiableModel):
    """Device."""

    class Meta:
        db_table = "canvas_sdk_data_api_device_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="devices", null=True
    )
    note_id = models.BigIntegerField()
    deleted = models.BooleanField()
    labeled_contains_NRL = models.BooleanField()
    assigning_authority = models.CharField(max_length=255)
    scoping_entity = models.CharField(max_length=255)
    udi = models.CharField(max_length=255)
    di = models.CharField(max_length=255)
    issuing_agency = models.CharField(max_length=255)
    lot_number = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=255)
    mri_safety_status = models.CharField(max_length=255)
    version_model_number = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    gmdnPTName = models.TextField()
    status = models.CharField(max_length=20)
    expiration_date = models.DateField()
    expiration_date_original = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=255)
    manufacturing_date_original = models.CharField(max_length=255)
    manufacturing_date = models.DateField()
    manufacturer = models.CharField(max_length=255)
    procedure_id = models.BigIntegerField()


__exports__ = ("Device",)

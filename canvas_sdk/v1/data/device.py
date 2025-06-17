from django.db import models


class Device(models.Model):
    """Device."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_device_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="devices", null=True
    )
    note_id = models.BigIntegerField()
    deleted = models.BooleanField()
    labeled_contains_NRL = models.BooleanField()
    assigning_authority = models.CharField()
    scoping_entity = models.CharField()
    udi = models.CharField()
    di = models.CharField()
    issuing_agency = models.CharField()
    lot_number = models.CharField()
    brand_name = models.CharField()
    mri_safety_status = models.CharField()
    version_model_number = models.CharField()
    company_name = models.CharField()
    gmdnPTName = models.TextField()
    status = models.CharField()
    expiration_date = models.DateField()
    expiration_date_original = models.CharField()
    serial_number = models.CharField()
    manufacturing_date_original = models.CharField()
    manufacturing_date = models.DateField()
    manufacturer = models.CharField()
    procedure_id = models.BigIntegerField()


__exports__ = ("Device",)

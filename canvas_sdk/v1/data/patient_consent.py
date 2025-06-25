from django.db import models


class PatientConsentRejectionCoding(models.Model):
    """Patient Consent Rejection Coding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientconsentrejectioncoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()


class PatientConsentExpirationRule(models.TextChoices):
    """PatientConsentExpirationRule."""

    NEVER = "never", "Never"
    IN_ONE_YEAR = "in_one_year", "In one year"
    END_OF_YEAR = "end_of_year", "End of year"


class PatientConsentCoding(models.Model):
    """Patient Consent Coding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientconsentcoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    expiration_rule = models.CharField(choices=PatientConsentExpirationRule, max_length=255)
    is_mandatory = models.BooleanField()
    is_proof_required = models.BooleanField()
    show_in_patient_portal = models.BooleanField()
    summary = models.TextField()


class PatientConsentStatus(models.TextChoices):
    """PatientConsentStatus."""

    ACCEPTED = "accepted", "Accepted"
    ACCEPTED_VIA_PORTAL = (
        "accepted_via_patient_portal",
        "Accepted Via Patient Portal",
    )
    REJECTED = "rejected", "Rejected"
    REJECTED_VIA_PORTAL = "rejected_via_patient_portal", "Rejected Via Patient Portal"


class PatientConsent(models.Model):
    """Patient Consent."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientconsent_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="patient_consent"
    )
    category = models.ForeignKey(
        "v1.PatientConsentCoding",
        on_delete=models.DO_NOTHING,
        related_name="patient_consent",
    )
    state = models.CharField(choices=PatientConsentStatus, max_length=255)
    effective_date = models.DateField()
    expired_date = models.DateField()
    rejection_reason = models.ForeignKey(
        "v1.PatientConsentRejectionCoding",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="patient_consents",
    )
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")


__exports__ = (
    "PatientConsent",
    "PatientConsentCoding",
    "PatientConsentRejectionCoding",
)

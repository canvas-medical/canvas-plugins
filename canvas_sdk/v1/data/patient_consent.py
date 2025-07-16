from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model


class PatientConsentRejectionCoding(Model):
    """Patient Consent Rejection Coding."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientconsentrejectioncoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()


class PatientConsentExpirationRule(models.TextChoices):
    """PatientConsentExpirationRule."""

    NEVER = "never", "Never"
    IN_ONE_YEAR = "in_one_year", "In one year"
    END_OF_YEAR = "end_of_year", "End of year"


class PatientConsentCoding(Model):
    """Patient Consent Coding."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientconsentcoding_001"

    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    display = models.CharField(max_length=1000)
    user_selected = models.BooleanField()
    expiration_rule = models.CharField(choices=PatientConsentExpirationRule.choices, max_length=255)
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


class PatientConsent(IdentifiableModel):
    """Patient Consent."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientconsent_001"

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

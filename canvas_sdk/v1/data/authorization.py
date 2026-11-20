from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
    Model,
)


class Authorization(AuditedModel, IdentifiableModel):
    """A payer's prior authorization for a patient, with the charges and diagnoses it covers."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_authorization_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="authorizations"
    )
    coverage = models.ForeignKey(
        "v1.Coverage", on_delete=models.DO_NOTHING, related_name="authorizations", null=True
    )
    # The column is varchar with no length, which CharField cannot declare on every backend.
    authorization_number = models.TextField()
    start_date = models.DateField(null=True)
    expiration_date = models.DateField(null=True)
    charges = models.ManyToManyField(
        "v1.ChargeDescriptionMaster",
        related_name="authorizations",
        db_table="canvas_sdk_data_quality_and_revenue_authorization_charges_001",
    )
    referring_provider_first_name = models.CharField(max_length=255, blank=True, default="")
    referring_provider_last_name = models.CharField(max_length=255, blank=True, default="")
    referring_provider_npi = models.CharField(max_length=255, blank=True, default="")
    notes = models.CharField(max_length=3000, blank=True, default="")
    visits_approved = models.IntegerField(blank=True, default=0)
    unlimited_visits = models.BooleanField(default=True)


class AuthorizationDiagnosisCode(Model):
    """A diagnosis code an authorization covers."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_authorizationcoding_001"

    authorization = models.ForeignKey(
        "v1.Authorization", on_delete=models.DO_NOTHING, related_name="codings"
    )
    code = models.CharField(max_length=20, blank=True)
    display = models.CharField(max_length=1000, blank=True)


__exports__ = (
    "Authorization",
    "AuthorizationDiagnosisCode",
)

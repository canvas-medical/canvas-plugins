from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel

# The target types a valid Provenance points at. Rows targeting anything else are invalid
# records left by an earlier writer, and the default manager hides them.
ALLOWED_TARGET_OBJECT_TYPES = frozenset(
    {
        "allergyintolerance",
        "careplan",
        "careteammembership",
        "condition",
        "consolidatedimmunization",
        "coverage",
        "device",
        "diagnosticreport",
        "documentreference",
        "encounter",
        "goal",
        "observation",
        "patient",
        "prescription",
        "procedure",
        "servicerequest",
        "updategoal",
    }
)


class ProvenanceAction(models.TextChoices):
    """The action a Provenance records."""

    CREATED = "CREATED", "created"
    UPDATED = "UPDATED", "updated"
    DELETED = "DELETED", "deleted"


class ProvenanceParticipantType(models.TextChoices):
    """The FHIR provenance participant type of a Provenance's agent."""

    ENTERER = "enterer", "Enterer"
    PERFORMER = "performer", "Performer"
    AUTHOR = "author", "Author"
    VERIFIER = "verifier", "Verifier"
    LEGAL = "legal", "Legal Authenticator"
    ATTESTER = "attester", "Attester"
    INFORMANT = "informant", "Informant"
    CUSTODIAN = "custodian", "Custodian"
    ASSEMBLER = "assembler", "Assembler"
    COMPOSER = "composer", "Composer"
    TRANSMITTER = "transmitter", "Transmitter"


class ProvenanceManager(models.Manager["Provenance"]):
    """Hides Provenance rows whose target type is not one a valid Provenance points at."""

    def get_queryset(self) -> models.QuerySet["Provenance"]:
        """Return only Provenance rows with an allowed target type."""
        return (
            super().get_queryset().filter(target_object_type__model__in=ALLOWED_TARGET_OBJECT_TYPES)
        )


class Provenance(TimestampedModel, IdentifiableModel):
    """A FHIR Provenance record: who did what to a record, when, and on whose behalf.

    The target, agent and on-behalf-of are generic links, each a content type plus an
    object id.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_provenance_001"

    objects = ProvenanceManager()

    target_object_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    target_object_id = models.IntegerField(null=True)
    occurred_date_time = models.DateTimeField(null=True)
    agent_object_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    agent_object_id = models.IntegerField(null=True)
    agent_participation_type = models.TextField(
        choices=ProvenanceParticipantType.choices, default="", blank=True
    )
    on_behalf_of_object_id = models.IntegerField(null=True)
    on_behalf_of_object_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    action = models.TextField(choices=ProvenanceAction.choices)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="provenance_set", null=True
    )


__exports__ = ("Provenance", "ProvenanceAction", "ProvenanceParticipantType")

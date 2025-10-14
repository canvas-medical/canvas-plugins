from django.db import models
from django.utils import timezone

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class EncounterMedium(models.TextChoices):
    """Encounter medium."""

    VOICE = "voice", "Telephone visit"
    VIDEO = "video", "Video visit"
    OFFICE = "office", "Office visit"
    HOME = "home", "Home visit"
    OFFSITE = "offsite", "Other offsite visit"
    LAB = "lab", "Lab visit"


class EncounterState(models.TextChoices):
    """Encounter state."""

    STARTED = "STA", "Started"
    PLANNED = "PLA", "Planned"
    CONCLUDED = "CON", "Concluded"
    CANCELLED = "CAN", "Cancelled"


class Encounter(TimestampedModel, IdentifiableModel):
    """Encounter."""

    class Meta:
        db_table = "canvas_sdk_data_api_encounter_001"

    note = models.OneToOneField("v1.Note", on_delete=models.CASCADE, related_name="encounter")
    medium = models.CharField(choices=EncounterMedium.choices, max_length=20)
    state = models.CharField(max_length=3, choices=EncounterState.choices)
    start_time = models.DateTimeField(default=timezone.now, null=True)
    end_time = models.DateTimeField(default=None, null=True)


__exports__ = (
    "Encounter",
    "EncounterMedium",
    "EncounterState",
)

from django.db import models
from django.db.models import TextChoices


class CompoundMedication(models.Model):
    """CompoundMedication."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_compoundmedication_001"

    class PotencyUnits(TextChoices):
        """Potency Units."""

        APPLICATOR = "C62412", "Applicator"
        BLISTER = "C54564", "Blister"
        CAPLET = "C64696", "Caplet"
        CAPSULE = "C48480", "Capsule"
        EACH = "C64933", "Each"
        FILM = "C53499", "Film"
        GRAM = "C48155", "Gram"
        GUM = "C69124", "Gum"
        IMPLANT = "C48499", "Implant"
        INSERT = "C62276", "Insert"
        KIT = "C48504", "Kit"
        LANCET = "C120263", "Lancet"
        LOZENGE = "C48506", "Lozenge"
        MILLILITER = "C28254", "Milliliter"
        PACKET = "C48521", "Packet"
        PAD = "C65032", "Pad"
        PATCH = "C48524", "Patch"
        PEN_NEEDLE = "C120216", "Pen Needle"
        RING = "C62609", "Ring"
        SPONGE = "C53502", "Sponge"
        STICK = "C53503", "Stick"
        STRIP = "C48538", "Strip"
        SUPPOSITORY = "C48539", "Suppository"
        SWAB = "C53504", "Swab"
        TABLET = "C48542", "Tablet"
        TROCHE = "C48548", "Troche"
        UNSPECIFIED = "C38046", "Unspecified"
        WAFER = "C48552", "Wafer"

    class ControlledSubstanceOptions(TextChoices):
        """Controlled Substance Options."""

        SCHEDULE_NOT_SCHEDULED = "N", "None"
        SCHEDULE_II = "II", "Schedule II"
        SCHEDULE_III = "III", "Schedule III"
        SCHEDULE_IV = "IV", "Schedule IV"
        SCHEDULE_V = "V", "Schedule V"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    active = models.BooleanField(default=True)
    formulation = models.CharField(max_length=105)
    potency_unit_code = models.CharField(max_length=20, choices=PotencyUnits.choices)
    controlled_substance = models.CharField(
        max_length=3, choices=ControlledSubstanceOptions.choices
    )
    controlled_substance_ndc = models.CharField(max_length=20, blank=True, default="")

    def __str__(self) -> str:
        return f'CompoundMedication: "{self.formulation}"'


__exports__ = ("CompoundMedication",)

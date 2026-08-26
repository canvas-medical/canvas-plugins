from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class VaccineManufacturer(models.TextChoices):
    """MVX manufacturer codes, as published by the CDC.

    Declared as the choices for ``mvx_code`` so ``get_mvx_code_display()`` returns the
    manufacturer name.
    """

    ASTRAZENECA = "ASZ", "AstraZeneca"
    BHARAT_BIOTECH_INTERNATIONAL_LIMITED = "BBI", "Bharat Biotech International Limited"
    BAVARIAN_NORDIC = "BN", "Bavarian Nordic A/S"
    BIOTEST_PHARMACEUTICALS_CORPORATION = "BTP", "Biotest Pharmaceuticals Corporation"
    CANSINO_BIOLOGICS = "CAN", "CanSino Biologics, Inc"
    DYNPORT_VACCINE_COMPANY = "DVC", "DynPort Vaccine Company, LLC"
    DYNAVAX = "DVX", "Dynavax, Inc"
    GEOVAX_LABS = "GEO", "GeoVax Labs, Inc"
    GRIFOLS = "GRF", "Grifols"
    ID_BIOMEDICAL = "IDB", "ID Biomedical"
    JOHNSON_AND_JOHNSON = "JNJ", "Johnson and Johnson"
    JANSSEN = "JSN", "Janssen"
    KEDRION_BIOPHARMA = "KED", "Kedrion Biopharma"
    KOREA_GREEN_CROSS_CORPORATION = "KGC", "Korea Green Cross Corporation"
    MASSACHUSETTS_BIOLOGIC_LABORATORIES = "MBL", "Massachusetts Biologic Laboratories"
    MEDICAGO = "MDO", "Medicago, Inc"
    MEDIMMUNE = "MED", "MedImmune, Inc. (AstraZeneca)"
    EMERGENT_BIOSOLUTIONS = "MIP", "Emergent BioSolutions"
    MODERNA_US = "MOD", "Moderna US, Inc"
    MERCK_AND_CO = "MSD", "Merck and Co., Inc"
    MSP_VACCINE_COMPANY = "MSP", "MSP Vaccine Company - (partnership Merck and Sanofi Pasteur)"
    NABI = "NAB", "NABI"
    NOVAVAX = "NVX", "Novavax, Inc"
    OTHER_MANUFACTURER = "OTH", "Other manufacturer"
    EMERGENT_TRAVEL_HEALTH = "PAX", "Emergent Travel Health, Inc (Formerly PaxVax)"
    PFIZER = "PFR", "Pfizer, Inc"
    SANOFI_PASTEUR = "PMC", "Sanofi Pasteur"
    PROTEIN_SCIENCES = "PSC", "Protein Sciences"
    SEQIRUS = "SEQ", "Seqirus"
    GLAXOSMITHKLINE = "SKB", "GlaxoSmithKline"
    SINOVAC = "SNV", "Sinovac "
    SINOPHARM_BIOTECH = "SPH", "Sinopharm-Biotech"
    TEVA_PHARMACEUTICALS_USA = "TVA", "TEVA Pharmaceuticals USA"
    UNKNOWN_MANUFACTURER = "UNK", "Unknown manufacturer"
    VALNEVA = "VAL", "Valneva"
    VBI_VACCINES_INC = "VBI", "VBI Vaccines, Inc"
    WYETH = "WAL", "Wyeth"


class Vaccine(TimestampedModel, IdentifiableModel):
    """A vaccine that can be administered."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_vaccine_001"

    payer = models.ForeignKey(
        "v1.Transactor", on_delete=models.DO_NOTHING, related_name="vaccines", null=True
    )
    charges = models.ManyToManyField(
        "v1.ChargeDescriptionMaster",
        related_name="vaccines",
        db_table="canvas_sdk_data_quality_and_revenue_vaccine_charges_001",
    )
    cvx_code = models.CharField(max_length=10)
    name = models.CharField(max_length=17000)
    short_name = models.CharField(max_length=17000)
    inventory = models.CharField(max_length=100)
    ndc_code = models.CharField(max_length=255)
    mvx_code = models.CharField(max_length=255, choices=VaccineManufacturer.choices)
    route = models.CharField(max_length=255)
    active = models.BooleanField()
    units = models.IntegerField()


class VaccineLot(TimestampedModel, IdentifiableModel):
    """A lot of a vaccine held in inventory."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_vaccinelot_001"

    vaccine = models.ForeignKey(
        Vaccine, on_delete=models.DO_NOTHING, related_name="lots", null=True
    )
    lot_number = models.CharField(max_length=255)
    ndc_code = models.CharField(max_length=255)
    mvx_code = models.CharField(max_length=255, choices=VaccineManufacturer.choices)
    expiration_date = models.DateField(null=True)
    diluent_lot_number = models.CharField(max_length=255)
    diluent_expiration_date = models.DateField(null=True)
    starting_inventory = models.PositiveIntegerField()
    quantity_adjustment = models.IntegerField()
    adjustment_notes = models.TextField()
    on_hand_inventory = models.IntegerField()
    used_inventory = models.PositiveIntegerField()


__exports__ = (
    "Vaccine",
    "VaccineLot",
    "VaccineManufacturer",
)

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model, TimestampedModel
from canvas_sdk.v1.data.common import AddressState, AddressType, AddressUse, TaxIDType


class PracticeLocationPOS(models.TextChoices):
    """PracticeLocationPOS choices."""

    PHARMACY = "01", "Pharmacy"
    TELEHEALTH = "02", "Telehealth"
    SCHOOL = "03", "Education Facility"
    HOMELESS_SHELTER = "04", "Homeless Shelter"
    PRISON = "09", "Prison"
    TELEHEALTH_IN_PATIENT_HOME = "10", "Telehealth in Patient's Home"
    OFFICE = "11", "Office"
    HOME = "12", "Home"
    ASSISTED_LIVING = "13", "Asssisted Living Facility"
    GROUP_HOME = "14", "Group Home"
    MOBILE = "15", "Mobile Unit"
    WALK_IN_RETAIL = "17", "Walk-In Retail Health Clinic"
    OFF_CAMPUS_OUTPATIENT_HOSPITAL = "19", "Off-Campus Outpatient Hospital"
    URGENT_CARE = "20", "Urgent Care Facility"
    INPATIENT_HOSPITAL = "21", "Inpatient Hospital"
    ON_CAMPUS_OUTPATIENT_HOSPITAL = "22", "On-Campus Outpatient Hospital"
    ER_HOSPITAL = "23", "Emergency Room Hospital"
    AMBULATORY_SURGERY_CENTER = "24", "Ambulatory Surgery Center"
    BIRTHING_CENTER = "25", "Birthing Center"
    MILITARY_FACILITY = "26", "Military Treatment Facility"
    STREET = "27", "Outreach Site / Street"
    SNF = "31", "Skilled Nursing Facility"
    NURSING = "32", "Nursing Facility"
    CUSTODIAL = "33", "Custodial Care Facility"
    HOSPICE = "34", "Hospice"
    AMBULANCE_LAND = "41", "Ambulance Land"
    AMBULANCE_AIR_WATER = "42", "Ambulance Air or Water"
    INDEPENDENT_CLINIC = "49", "Independent Clinic"
    FQHC = "50", "Federally Qualified Health Center"
    PSYCH = "51", "Inpatient Psychiatric Facility"
    PSYCH_PARTIAL = "52", "Inpatient Psychiatric Facility - Partial Hospitalization"
    MENTAL_HEALTH_CENTER = "53", "Community Mental Health Center"
    INTERMEDIATE_MENTAL = "54", "Intermediate Care Facility for Mentally Retarded"
    SUBSTANCE_RESIDENTIAL = "55", "Residential Substance Abuse Treatment Facility"
    PSYCH_RESIDENTIAL = "56", "Psychiatric Residential Treatment Center"
    SUBSTANCE_NON_RESIDENTIAL = "57", "Non-Residential Substance Abuse Treatment Facility"
    MASS_IMMUNIZATION = "60", "Mass Immunization Center"
    INPATIENT_REHAB = "61", "Inpatient Rehabilitation Facility"
    OUTPATIENT_REHAB = "62", "Outpatient Rehabilitation Facility"
    ESRD = "65", "End-Stage Renal Disease Treatment Facility"
    PUBLIC_CLINIC = "71", "State or Local Public Health Clinic"
    RURAL_CLINIC = "72", "Rural Health Clinic"
    INDEPENDENT_LAB = "81", "Independent Laboratory"
    OTHER = "99", "Other Place of Service"


class PracticeLocation(TimestampedModel, IdentifiableModel):
    """PracticeLocation."""

    class Meta:
        db_table = "canvas_sdk_data_api_practicelocation_001"

    organization = models.ForeignKey(
        "v1.Organization", on_delete=models.DO_NOTHING, related_name="practice_locations", null=True
    )
    place_of_service_code = models.CharField(choices=PracticeLocationPOS.choices, max_length=2)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    background_image_url = models.CharField(max_length=255)
    background_gradient = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    npi_number = models.CharField(max_length=10)
    bill_through_organization = models.BooleanField()
    tax_id = models.CharField(max_length=25)
    tax_id_type = models.CharField(choices=TaxIDType.choices, max_length=1)
    billing_location_name = models.CharField(max_length=255)
    group_npi_number = models.CharField(max_length=10)
    taxonomy_number = models.CharField(max_length=10)
    include_zz_qualifier = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.full_name


class PracticeLocationAddress(Model):
    """PracticeLocationAddress."""

    class Meta:
        db_table = "canvas_sdk_data_api_practicelocationaddress_001"

    practice_location = models.ForeignKey(
        "v1.PracticeLocation", on_delete=models.DO_NOTHING, related_name="addresses", null=True
    )
    line1 = models.CharField(max_length=255, default="", blank=True)
    line2 = models.CharField(max_length=255, default="", blank=True)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255, blank=True, default="")
    state_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=255)
    use = models.CharField(choices=AddressUse.choices, max_length=10, default=AddressUse.WORK)
    type = models.CharField(choices=AddressType.choices, max_length=10, default=AddressType.BOTH)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=255)
    state = models.CharField(
        choices=AddressState.choices, max_length=20, default=AddressState.ACTIVE
    )

    def __str__(self) -> str:
        return f"Address for {self.practice_location}"


class PracticeLocationSetting(Model):
    """PracticeLocationSetting."""

    class Meta:
        db_table = "canvas_sdk_data_api_practicelocationsetting_001"

    practice_location = models.ForeignKey(
        "v1.PracticeLocation", on_delete=models.DO_NOTHING, related_name="settings", null=True
    )
    name = models.CharField(max_length=100)
    value = models.JSONField()

    def __str__(self) -> str:
        return self.name


__exports__ = (
    "PracticeLocationPOS",
    "PracticeLocation",
    "PracticeLocationSetting",
    "PracticeLocationAddress",
)

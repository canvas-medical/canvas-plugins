from django.db import models

from canvas_sdk.v1.data.common import TaxIDType


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


class PracticeLocation(models.Model):
    """PracticeLocation."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_practicelocation_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    organization = models.ForeignKey(
        "v1.Organization", on_delete=models.DO_NOTHING, related_name="practice_locations", null=True
    )
    place_of_service_code = models.CharField(choices=PracticeLocationPOS.choices)
    full_name = models.CharField()
    short_name = models.CharField()
    background_image_url = models.CharField()
    background_gradient = models.CharField()
    active = models.BooleanField()
    npi_number = models.CharField()
    bill_through_organization = models.BooleanField()
    tax_id = models.CharField()
    tax_id_type = models.CharField(choices=TaxIDType.choices)
    billing_location_name = models.CharField()
    group_npi_number = models.CharField()
    taxonomy_number = models.CharField()
    include_zz_qualifier = models.BooleanField()

    def __str__(self) -> str:
        return self.full_name


class PracticeLocationSetting(models.Model):
    """PracticeLocationSetting."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_practicelocationsetting_001"

    dbid = models.BigIntegerField(primary_key=True)
    practice_location = models.ForeignKey(
        "v1.PracticeLocation", on_delete=models.DO_NOTHING, related_name="settings", null=True
    )
    name = models.CharField()
    value = models.JSONField()

    def __str__(self) -> str:
        return self.name


__exports__ = (
    "PracticeLocationPOS",
    "PracticeLocation",
    "PracticeLocationSetting",
)

from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.patient import Patient

# from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.user import CanvasUser


class NoteType(models.Model):
    """NoteType."""

    class NoteTypeCategories:
        MESSAGE = "message"
        LETTER = "letter"
        INPATIENT = "inpatient"
        REVIEW = "review"
        ENCOUNTER = "encounter"
        APPOINTMENT = "appointment"
        SEARCH = "search"
        TASK = "task"
        DATA = "data"
        CCDA = "ccda"
        SCHEDULE_EVENT = "schedule_event"

        CHOICES = {
            MESSAGE: "Message",
            LETTER: "Letter",
            INPATIENT: "Inpatient Visit Note",
            REVIEW: "Chart Review Note",
            ENCOUNTER: "Encounter Note",
            APPOINTMENT: "Appointment Note",
            TASK: "Task",
            DATA: "Data",
            CCDA: "C-CDA",
            SCHEDULE_EVENT: "Schedule Event",
        }

    class PracticeLocationPOS:
        PHARMACY = "01"
        TELEHEALTH = "02"
        SCHOOL = "03"
        HOMELESS_SHELTER = "04"
        PRISON = "09"
        TELEHEALTH_IN_PATIENT_HOME = "10"
        OFFICE = "11"
        HOME = "12"
        ASSISTED_LIVING = "13"
        GROUP_HOME = "14"
        MOBILE = "15"
        WALK_IN_RETAIL = "17"
        OFF_CAMPUS_OUTPATIENT_HOSPITAL = "19"
        URGENT_CARE = "20"
        INPATIENT_HOSPITAL = "21"
        ON_CAMPUS_OUTPATIENT_HOSPITAL = "22"
        ER_HOSPITAL = "23"
        AMBULATORY_SURGERY_CENTER = "24"
        BIRTHING_CENTER = "25"
        MILITARY_FACILITY = "26"
        STREET = "27"
        SNF = "31"
        NURSING = "32"
        CUSTODIAL = "33"
        HOSPICE = "34"
        AMBULANCE_LAND = "41"
        AMBULANCE_AIR_WATER = "42"
        INDEPENDENT_CLINIC = "49"
        FQHC = "50"
        PSYCH = "51"
        PSYCH_PARTIAL = "52"
        MENTAL_HEALTH_CENTER = "53"
        INTERMEDIATE_MENTAL = "54"
        SUBSTANCE_RESIDENTIAL = "55"
        PSYCH_RESIDENTIAL = "56"
        SUBSTANCE_NON_RESIDENTIAL = "57"
        MASS_IMMUNIZATION = "60"
        INPATIENT_REHAB = "61"
        OUTPATIENT_REHAB = "62"
        ESRD = "65"
        PUBLIC_CLINIC = "71"
        RURAL_CLINIC = "72"
        INDEPENDENT_LAB = "81"
        OTHER = "99"

        CHOICES = {
            PHARMACY: "Pharmacy",
            TELEHEALTH: "Telehealth",
            SCHOOL: "Education Facility",
            HOMELESS_SHELTER: "Homeless Shelter",
            PRISON: "Prison",
            ASSISTED_LIVING: "Asssisted Living Facility",
            GROUP_HOME: "Group Home",
            WALK_IN_RETAIL: "Walk-In Retail Health Clinic",
            OFF_CAMPUS_OUTPATIENT_HOSPITAL: "Off-Campus Outpatient Hospital",
            INPATIENT_HOSPITAL: "Inpatient Hospital",
            ON_CAMPUS_OUTPATIENT_HOSPITAL: "On-Campus Outpatient Hospital",
            ER_HOSPITAL: "Emergency Room Hospital",
            AMBULATORY_SURGERY_CENTER: "Ambulatory Surgery Center",
            MILITARY_FACILITY: "Military Treatment Facility",
            STREET: "Outreach Site / Street",
            SNF: "Skilled Nursing Facility",
            CUSTODIAL: "Custodial Care Facility",
            HOSPICE: "Hospice",
            AMBULANCE_LAND: "Ambulance Land",
            AMBULANCE_AIR_WATER: "Ambulance Air or Water",
            PSYCH: "Inpatient Psychiatric Facility",
            PSYCH_PARTIAL: "Inpatient Psychiatric Facility - Partial Hospitalization",
            MENTAL_HEALTH_CENTER: "Community Mental Health Center",
            INTERMEDIATE_MENTAL: "Intermediate Care Facility for Mentally Retarded",
            SUBSTANCE_RESIDENTIAL: "Residential Substance Abuse Treatment Facility",
            PSYCH_RESIDENTIAL: "Psychiatric Residential Treatment Center",
            SUBSTANCE_NON_RESIDENTIAL: "Non-Residential Substance Abuse Treatment Facility",
            INPATIENT_REHAB: "Inpatient Rehabilitation Facility",
            OUTPATIENT_REHAB: "Outpatient Rehabilitation Facility",
            OFFICE: "Office",
            HOME: "Home",
            MOBILE: "Mobile Unit",
            URGENT_CARE: "Urgent Care Facility",
            BIRTHING_CENTER: "Birthing Center",
            NURSING: "Nursing Facility",
            INDEPENDENT_CLINIC: "Independent Clinic",
            FQHC: "Federally Qualified Health Center",
            MASS_IMMUNIZATION: "Mass Immunization Center",
            ESRD: "End-Stage Renal Disease Treatment Facility",
            PUBLIC_CLINIC: "State or Local Public Health Clinic",
            RURAL_CLINIC: "Rural Health Clinic",
            INDEPENDENT_LAB: "Independent Laboratory",
            OTHER: "Other Place of Service",
            TELEHEALTH_IN_PATIENT_HOME: "Telehealth in Patient's Home",
        }

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_notetype_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    name = models.CharField()
    icon = models.CharField()
    category = models.CharField(choices=NoteTypeCategories.CHOICES)
    rank = models.PositiveIntegerField()
    is_default_appointment_type = models.BooleanField()
    is_scheduleable = models.BooleanField()
    is_telehealth = models.BooleanField()
    is_billable = models.BooleanField()
    defer_place_of_service_to_practice_location = models.BooleanField()
    available_places_of_service = ArrayField(models.CharField(choices=PracticeLocationPOS.CHOICES))
    default_place_of_service = models.CharField(choices=PracticeLocationPOS.CHOICES)
    is_system_managed = models.BooleanField()
    is_visible = models.BooleanField()
    is_active = models.BooleanField()
    unique_identifier = models.UUIDField()
    deprecated_at = models.DateTimeField()
    is_patient_required = models.BooleanField()
    allow_custom_title = models.BooleanField()


class Note(models.Model):
    """Note."""

    class NoteType:
        MESSAGE = "message"
        LETTER = "letter"
        INPATIENT = "inpatient"
        REVIEW = "review"
        VOICE = "voice"
        VIDEO = "video"
        OFFICE = "office"
        LAB = "lab"
        HOME = "home"
        GROUP = "group"
        APPOINTMENT = "appointment"
        OFFSITE = "offsite"
        SEARCH = "search"
        TASK = "task"
        DATA = "data"
        CCDA = "ccda"

        CHOICES = {
            MESSAGE: "Message",
            LETTER: "Letter",
            INPATIENT: "Inpatient Visit Note",
            REVIEW: "Chart Review Note",
            VOICE: "Phone Call Note",
            VIDEO: "Video Call Note",
            OFFICE: "Office Visit Note",
            LAB: "Lab Visit Note",
            HOME: "Home Visit Note",
            APPOINTMENT: "Appointment Note",
            GROUP: "Group Visit Note",
            OFFSITE: "Other Offsite Visit Note",
            SEARCH: "Search",
            TASK: "Task",
            DATA: "Data",
            CCDA: "C-CDA Import",
        }

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_note_001"

    id = models.CharField(max_length=32)
    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    # provider = models.ForeignKey(Staff, on_delete=models.DO_NOTHING, related_name="notes")
    note_type = models.CharField(choices=NoteType.CHOICES, null=True)
    note_type_version = models.ForeignKey(
        "NoteType", on_delete=models.DO_NOTHING, related_name="notes"
    )
    title = models.TextField()
    body = models.JSONField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    # last_modified_by_staff = models.ForeignKey(Staff, on_delete=models.DO_NOTHING, null=True)
    checksum = models.CharField()
    billing_note = models.TextField()
    # TODO -implement InpatientStay model
    # inpatient_stay = models.ForeignKey("InpatientStay", on_delete=models.DO_NOTHING)
    related_data = models.JSONField()
    # TODO -implement PracticeLocation model
    # location = models.ForeignKey(PracticeLocation, on_delete=models.DO_NOTHING)
    datetime_of_service = models.DateTimeField()
    place_of_service = models.CharField()

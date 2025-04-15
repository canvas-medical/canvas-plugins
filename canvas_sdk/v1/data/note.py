from django.contrib.postgres.fields import ArrayField
from django.db import models


class NoteTypeCategories(models.TextChoices):
    """Note type categories."""

    MESSAGE = "message", "Message"
    LETTER = "letter", "Letter"
    INPATIENT = "inpatient", "Inpatient Visit Note"
    REVIEW = "review", "Chart Review Note"
    ENCOUNTER = "encounter", "Encounter Note"
    APPOINTMENT = "appointment", "Appointment Note"
    TASK = "task", "Task"
    DATA = "data", "Data"
    CCDA = "ccda", "C-CDA"
    SCHEDULE_EVENT = "schedule_event", "Schedule Event"


class PracticeLocationPOS(models.TextChoices):
    """Practice Location POS."""

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


class NoteTypes(models.TextChoices):
    """Note types."""

    MESSAGE = "message", "Message"
    LETTER = "letter", "Letter"
    INPATIENT = "inpatient", "Inpatient Visit Note"
    REVIEW = "review", "Chart Review Note"
    VOICE = "voice", "Phone Call Note"
    VIDEO = "video", "Video Call Note"
    OFFICE = "office", "Office Visit Note"
    LAB = "lab", "Lab Visit Note"
    HOME = "home", "Home Visit Note"
    GROUP = "group", "Group Visit Note"
    APPOINTMENT = "appointment", "Appointment Note"
    OFFSITE = "offsite", "Other Offsite Visit Note"
    SEARCH = "search", "Search"
    TASK = "task", "Task"
    DATA = "data", "Data"
    CCDA = "ccda", "C-CDA Import"


class NoteType(models.Model):
    """NoteType."""

    objects: models.Manager["NoteType"]

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_notetype_001"

    id = models.UUIDField()
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
    category = models.CharField(choices=NoteTypeCategories.choices)
    rank = models.PositiveIntegerField()
    is_default_appointment_type = models.BooleanField()
    is_scheduleable = models.BooleanField()
    is_telehealth = models.BooleanField()
    is_billable = models.BooleanField()
    defer_place_of_service_to_practice_location = models.BooleanField()
    available_places_of_service = ArrayField(models.CharField(choices=PracticeLocationPOS.choices))
    default_place_of_service = models.CharField(choices=PracticeLocationPOS.choices)
    is_system_managed = models.BooleanField()
    is_visible = models.BooleanField()
    is_active = models.BooleanField()
    unique_identifier = models.UUIDField()
    deprecated_at = models.DateTimeField()
    is_patient_required = models.BooleanField()
    allow_custom_title = models.BooleanField()
    is_scheduleable_via_patient_portal = models.BooleanField()
    online_duration = models.IntegerField()


class Note(models.Model):
    """Note."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_note_001"

    id = models.CharField(max_length=32)
    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="notes", null=True
    )
    provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="notes", null=True
    )
    note_type = models.CharField(choices=NoteTypes.choices, null=True)
    note_type_version = models.ForeignKey(
        "v1.NoteType", on_delete=models.DO_NOTHING, related_name="notes", null=True
    )
    title = models.TextField()
    body = models.JSONField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    last_modified_by_staff = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, null=True)
    checksum = models.CharField()
    billing_note = models.TextField()
    # TODO -implement InpatientStay model
    # inpatient_stay = models.ForeignKey("v1.InpatientStay", on_delete=models.DO_NOTHING, null=True)
    related_data = models.JSONField()
    location = models.ForeignKey("v1.PracticeLocation", on_delete=models.DO_NOTHING, null=True)
    datetime_of_service = models.DateTimeField()
    place_of_service = models.CharField()


__exports__ = (
    "NoteTypeCategories",
    "PracticeLocationPOS",
    "NoteTypes",
    "NoteType",
    "Note",
)

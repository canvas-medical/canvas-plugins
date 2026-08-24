from typing import cast

from django.db import models
from django.utils import timezone

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)


class VitalSignChoices(models.TextChoices):
    """VitalSign choices."""

    SIGN_HEAD_CIRCUMFERENCE_TAPE_MEASURE = (
        "head_circumference_tape_measure",
        "Head Circumference by Tape Measure",
    )
    SIGN_HEAD_CIRCUMFERENCE = "head_circumference", "Head Circumference"
    SIGN_LAST_MENSTRUAL_PERIOD = "last_menstrual_period", "Last Menstrual Period"
    SIGN_PAIN_SEVERITY = "pain_severity", "Pain Severity"
    SIGN_WAIST_CIRCUMFERENCE = "waist_circumference", "Waist Circumference"
    SIGN_BLOOD_PRESSURE = "blood_pressure", "Blood Pressure"
    SIGN_SYSTOLE = "systole", "Systole"
    SIGN_DIASTOLE = "diastole", "Diastole"
    SIGN_WEIGHT = "weight", "Weight"
    SIGN_HEIGHT = "height", "Height"
    SIGN_LENGTH = "length", "Length"
    SIGN_BODY_TEMPERATURE = "body_temperature", "Body Temperature"
    SIGN_PULSE_RATE = "pulse", "Pulse"
    SIGN_PULSE_RHYTHM = "pulse_rhythm", "Pulse Rhythm"
    SIGN_OXYGEN_SATURATION_ARTERIAL = "oxygen_saturation_arterial", "Oxygen Saturation Arterial"
    SIGN_OXYGEN_SATURATION = "oxygen_saturation", "Oxygen Saturation"
    SIGN_INHALE_OXYGEN_CONCENTRATION = (
        "inhale_oxygen_concentration",
        "Inhaled Oxygen Concentration",
    )
    SIGN_OXYGEN_CONCENTRATION = "inhaled_oxygen_concentration", "Inhaled Oxygen Contentration"
    SIGN_INHALED_OXYGEN_FLOW_RATE = "inhaled_oxygen_flow_rate", "Inhaled Oxygen Flow Rate"
    SIGN_RESPIRATION_RATE = "respiration_rate", "Respiration Rate"
    SIGN_BMI = "bmi", "Body Mass Index"
    SIGN_BMI_PERCENTILE = "bmi_percentile", "BMI for Age Percentile"
    SIGN_NOTE = "note", "Note"
    SIGN_HEAD_CIRCUMFERENCE_PERCENTILE = (
        "head_circumference_percentile",
        "Head Occipital-frontal circumference Percentile",
    )
    SIGN_WEIGHT_FOR_LENGTH_PERCENTILE = (
        "weight_for_length_percentile",
        "Weight-for-Length Percentile",
    )
    SIGN_SUPPLEMENTAL_OXYGEN = "supplemental_oxygen", "Supplemental Oxygen"


class VitalSignReadingQuerySet(
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    BaseQuerySet,
):
    """VitalSignReadingQuerySet."""

    pass


VitalSignReadingManager = BaseModelManager.from_queryset(VitalSignReadingQuerySet)


class VitalSignReading(AuditedModel, IdentifiableModel):
    """The anchor for a vitals command — a set of readings recorded on a note for a patient."""

    class Meta:
        db_table = "canvas_sdk_data_api_vitalsignreading_001"

    objects = cast(VitalSignReadingQuerySet, VitalSignReadingManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="vital_sign_readings"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="vital_sign_readings"
    )
    date_recorded = models.DateTimeField(default=timezone.now)


class VitalSign(TimestampedModel, IdentifiableModel):
    """A single vital-sign measurement (e.g. blood pressure) belonging to a VitalSignReading."""

    class Meta:
        db_table = "canvas_sdk_data_api_vitalsign_001"

    reading = models.ForeignKey(VitalSignReading, on_delete=models.DO_NOTHING, related_name="signs")
    date_recorded = models.DateTimeField(default=timezone.now, db_index=True)
    loinc_num = models.CharField(max_length=10)
    sign = models.CharField(choices=VitalSignChoices.choices, max_length=33, db_index=True)
    sign_description = models.CharField(max_length=100, blank=True, default="")
    value = models.CharField(max_length=150)
    units = models.CharField(max_length=50, blank=True, default="")
    source = models.CharField(max_length=255, blank=True, default="")
    parent = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, null=True, related_name="children"
    )


__exports__ = ("VitalSign", "VitalSignReading")

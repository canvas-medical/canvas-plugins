from __future__ import annotations

from typing import TYPE_CHECKING, Any

import arrow
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.common import (
    AddressState,
    AddressType,
    AddressUse,
    ContactPointState,
    ContactPointSystem,
    ContactPointUse,
)

if TYPE_CHECKING:
    from django_stubs_ext.db.models.manager import RelatedManager


class SexAtBirth(TextChoices):
    """SexAtBirth."""

    FEMALE = "F", "female"
    MALE = "M", "male"
    OTHER = "O", "other"
    UNKNOWN = "UNK", "unknown"
    BLANK = "", ""


class PatientSettingConstants:
    """PatientSettingConstants."""

    LAB = "lab"
    PHARMACY = "pharmacy"
    IMAGING_CENTER = "imagingCenter"
    CONTACT_METHOD = "contactMethod"
    PREFERRED_SCHEDULING_TIMEZONE = "preferredSchedulingTimezone"


class Patient(models.Model):
    """A class representing a patient."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patient_001"

    id = models.CharField(max_length=32, db_column="key")
    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    first_name = models.CharField()
    last_name = models.CharField()
    birth_date = models.DateField()
    sex_at_birth = models.CharField(choices=SexAtBirth.choices)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    prefix = models.CharField()
    suffix = models.CharField()
    middle_name = models.CharField()
    maiden_name = models.CharField()
    nickname = models.CharField()
    sexual_orientation_term = models.CharField()
    sexual_orientation_code = models.CharField()
    gender_identity_term = models.CharField()
    gender_identity_code = models.CharField()
    preferred_pronouns = models.CharField()
    biological_race_codes = ArrayField(models.CharField())
    last_known_timezone = models.CharField()
    mrn = models.CharField()
    active = models.BooleanField()
    deceased = models.BooleanField()
    deceased_datetime = models.DateTimeField()
    deceased_cause = models.TextField()
    deceased_comment = models.TextField()
    other_gender_description = models.CharField()
    social_security_number = models.CharField()
    administrative_note = models.TextField()
    clinical_note = models.TextField()
    mothers_maiden_name = models.CharField()
    multiple_birth_indicator = models.BooleanField()
    birth_order = models.BigIntegerField()
    default_location_id = models.BigIntegerField()
    default_provider_id = models.BigIntegerField()
    user = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)

    settings: RelatedManager[PatientSetting]

    @classmethod
    def find(cls, id: str) -> Patient:
        """Find a patient by id."""
        return cls._default_manager.get(id=id)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def age_at(self, time: arrow.Arrow) -> float:
        """Given a datetime, returns what the patient's age would be at that datetime."""
        age = float(0)
        birth_date = arrow.get(self.birth_date)
        if birth_date.date() < time.date():
            age = time.datetime.year - birth_date.datetime.year
            if time.datetime.month < birth_date.datetime.month or (
                time.datetime.month == birth_date.datetime.month
                and time.datetime.day < birth_date.datetime.day
            ):
                age -= 1

            current_year = birth_date.shift(years=age)
            next_year = birth_date.shift(years=age + 1)
            age += (time.date() - current_year.date()) / (next_year.date() - current_year.date())
        return age

    def get_setting(self, name: str) -> Any:
        """Returns a patient setting value by name."""
        try:
            return self.settings.get(name=name).value
        except PatientSetting.DoesNotExist:
            return None

    @property
    def preferred_pharmacy(self) -> dict[str, str] | None:
        """Returns the patient's preferred pharmacy."""
        pharmacy_setting = self.get_setting(PatientSettingConstants.PHARMACY) or {}
        if isinstance(pharmacy_setting, list):
            for pharmacy in pharmacy_setting:
                if pharmacy.get("default", False):
                    return pharmacy
            return None
        return pharmacy_setting


class PatientContactPoint(models.Model):
    """A class representing a patient contact point."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientcontactpoint_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField(choices=ContactPointSystem.choices)
    value = models.CharField()
    use = models.CharField(choices=ContactPointUse.choices)
    use_notes = models.CharField()
    rank = models.IntegerField()
    state = models.CharField(choices=ContactPointState.choices)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="telecom", null=True
    )
    has_consent = models.BooleanField()
    last_verified = models.DateTimeField
    verification_token = models.CharField()
    opted_out = models.BooleanField()


class PatientAddress(models.Model):
    """A class representing a patient address."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientaddress_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    line1 = models.CharField()
    line2 = models.CharField()
    city = models.CharField()
    district = models.CharField()
    state_code = models.CharField()
    postal_code = models.CharField()
    use = models.CharField(choices=AddressUse.choices)
    type = models.CharField(choices=AddressType.choices)
    longitude = models.FloatField()
    latitude = models.FloatField()
    start = models.DateField()
    end = models.DateField()
    country = models.CharField()
    state = models.CharField(choices=AddressState.choices)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="addresses", null=True
    )

    def __str__(self) -> str:
        return f"id={self.id}"


class PatientExternalIdentifier(models.Model):
    """A class representing a patient external identifier."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientexternalidentifier_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient", related_name="external_identifiers", on_delete=models.DO_NOTHING, null=True
    )
    use = models.CharField()
    identifier_type = models.CharField()
    system = models.CharField()
    value = models.CharField()
    issued_date = models.DateField()
    expiration_date = models.DateField()

    def __str__(self) -> str:
        return f"id={self.id}"


class PatientSetting(models.Model):
    """PatientSetting."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_patientsetting_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="settings", null=True
    )
    name = models.CharField()
    value = models.JSONField()


__exports__ = (
    "SexAtBirth",
    "PatientSettingConstants",
    "Patient",
    "PatientContactPoint",
    "PatientAddress",
    "PatientExternalIdentifier",
    "PatientSetting",
    # not defined here but used by current plugins
    "ContactPointState",
    "ContactPointSystem",
)

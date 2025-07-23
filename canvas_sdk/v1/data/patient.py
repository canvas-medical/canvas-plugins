from __future__ import annotations

from typing import TYPE_CHECKING, Any

import arrow
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import TextChoices

from canvas_sdk.v1.data.base import IdentifiableModel, Model
from canvas_sdk.v1.data.common import (
    AddressState,
    AddressType,
    AddressUse,
    ContactPointState,
    ContactPointSystem,
    ContactPointUse,
)
from canvas_sdk.v1.data.utils import create_key

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


class Patient(Model):
    """A class representing a patient."""

    class Meta:
        db_table = "canvas_sdk_data_api_patient_001"

    id = models.CharField(
        max_length=32, db_column="key", unique=True, editable=False, default=create_key
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    business_line = models.ForeignKey(
        "v1.BusinessLine", on_delete=models.DO_NOTHING, related_name="patients"
    )
    sex_at_birth = models.CharField(choices=SexAtBirth.choices, max_length=3)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    prefix = models.CharField(max_length=100)
    suffix = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=255)
    maiden_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    sexual_orientation_term = models.CharField(max_length=255)
    sexual_orientation_code = models.CharField(max_length=255)
    gender_identity_term = models.CharField(max_length=255)
    gender_identity_code = models.CharField(max_length=255)
    preferred_pronouns = models.CharField(max_length=255)
    biological_race_codes = ArrayField(models.CharField(max_length=100))
    last_known_timezone = models.CharField(max_length=32)
    mrn = models.CharField(max_length=9)
    active = models.BooleanField()
    deceased = models.BooleanField()
    deceased_datetime = models.DateTimeField()
    deceased_cause = models.TextField()
    deceased_comment = models.TextField()
    other_gender_description = models.CharField(max_length=255)
    social_security_number = models.CharField(max_length=9)
    administrative_note = models.TextField()
    clinical_note = models.TextField()
    mothers_maiden_name = models.CharField(max_length=255)
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

    @property
    def preferred_full_name(self) -> str:
        """Returns the patient's preferred full name, taking nickname into consideration."""
        return " ".join(n for n in (self.preferred_first_name, self.last_name, self.suffix) if n)

    @property
    def preferred_first_name(self) -> str:
        """Returns the patient's preferred first name, taking nickname into consideration."""
        return self.nickname or self.first_name


class PatientContactPoint(IdentifiableModel):
    """A class representing a patient contact point."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientcontactpoint_001"

    system = models.CharField(choices=ContactPointSystem.choices, max_length=20)
    value = models.CharField(max_length=100)
    use = models.CharField(choices=ContactPointUse.choices, max_length=20)
    use_notes = models.CharField(max_length=255)
    rank = models.IntegerField()
    state = models.CharField(choices=ContactPointState.choices, max_length=20)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="telecom", null=True
    )
    has_consent = models.BooleanField()
    last_verified = models.DateTimeField
    verification_token = models.CharField(max_length=32)
    opted_out = models.BooleanField()


class PatientAddress(IdentifiableModel):
    """A class representing a patient address."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientaddress_001"

    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=255)
    use = models.CharField(choices=AddressUse.choices, max_length=10)
    type = models.CharField(choices=AddressType.choices, max_length=10)
    longitude = models.FloatField()
    latitude = models.FloatField()
    start = models.DateField()
    end = models.DateField()
    country = models.CharField(max_length=255)
    state = models.CharField(choices=AddressState.choices, max_length=20)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="addresses", null=True
    )

    def __str__(self) -> str:
        return f"id={self.id}"


class PatientExternalIdentifier(IdentifiableModel):
    """A class representing a patient external identifier."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientexternalidentifier_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    patient = models.ForeignKey(
        "v1.Patient",
        related_name="external_identifiers",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    use = models.CharField(max_length=255)
    identifier_type = models.CharField(max_length=255)
    system = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    issued_date = models.DateField()
    expiration_date = models.DateField()

    def __str__(self) -> str:
        return f"id={self.id}"


class PatientSetting(Model):
    """PatientSetting."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientsetting_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="settings", null=True
    )
    name = models.CharField(max_length=100)
    value = models.JSONField()


class PatientMetadata(IdentifiableModel):
    """A class representing Patient Metadata."""

    class Meta:
        db_table = "canvas_sdk_data_api_patientmetadata_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="metadata", null=True
    )
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)


__exports__ = (
    "SexAtBirth",
    "PatientSettingConstants",
    "Patient",
    "PatientContactPoint",
    "PatientAddress",
    "PatientExternalIdentifier",
    "PatientSetting",
    "PatientMetadata",
    # not defined here but used by current plugins
    "ContactPointState",
    "ContactPointSystem",
)

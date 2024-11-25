from typing import TYPE_CHECKING, Self

import arrow
from django.db import models


class Patient(models.Model):
    """A class representing a patient."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_patient_001"

    id = models.CharField(max_length=32, db_column="key")
    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    first_name = models.CharField()
    last_name = models.CharField()
    birth_date = models.DateField()
    sex_at_birth = models.CharField()
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

    @classmethod
    def find(cls, id: str) -> Self:
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

from django.contrib.postgres.fields import ArrayField
from django.db import models
from timezone_utils.fields import TimeZoneField

from canvas_sdk.v1.data.common import PersonSex, TaxIDType
from canvas_sdk.v1.data.user import CanvasUser


class Staff(models.Model):
    """Staff."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_staff_001"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    id = models.CharField(max_length=32, db_column="key")
    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    prefix = models.CharField()
    suffix = models.CharField()
    first_name = models.CharField()
    middle_name = models.CharField()
    last_name = models.CharField()
    maiden_name = models.CharField()
    nickname = models.CharField()
    previous_names = models.JSONField()
    birth_date = models.DateField(null=True)
    sex_at_birth = models.CharField(choices=PersonSex.choices)
    sexual_orientation_term = models.CharField()
    sexual_orientation_code = models.CharField()
    gender_identity_term = models.CharField()
    gender_identity_code = models.CharField()
    preferred_pronouns = models.CharField()
    biological_race_codes = ArrayField(models.CharField())
    biological_race_terms = ArrayField(models.CharField())
    cultural_ethnicity_codes = ArrayField(models.CharField())
    cultural_ethnicity_terms = ArrayField(models.CharField())
    last_known_timezone = TimeZoneField(null=True)
    active = models.BooleanField()
    # TODO - uncomment when PracticeLocation field is developed
    # primary_practice_location = models.ForeignKey(
    #     PracticeLocation, on_delete=models.DO_NOTHING, null=True
    # )
    npi_number = models.CharField()
    nadean_number = models.CharField()
    group_npi_number = models.CharField()
    bill_through_organization = models.BooleanField()
    tax_id = models.CharField()
    tax_id_type = models.CharField(choices=TaxIDType.choices)
    spi_number = models.CharField()
    # TODO - uncomment when Language is developed
    # language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, related_name="staff_speakers")
    # language_secondary = models.ForeignKey(Language, on_delete=models.DO_NOTHING, related_name="staff_secondary_speakers")
    personal_meeting_room_link = models.URLField(null=True)
    state = models.JSONField()
    user = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    schedule_column_ordering = models.IntegerField()
    default_supervising_provider = models.ForeignKey(
        "Staff", on_delete=models.DO_NOTHING, null=True, related_name="supervising_team"
    )

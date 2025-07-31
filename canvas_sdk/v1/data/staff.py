from functools import cached_property

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.enums import TextChoices
from timezone_utils.fields import TimeZoneField

from canvas_sdk.v1.data.base import IdentifiableModel, Model
from canvas_sdk.v1.data.common import (
    AddressState,
    AddressType,
    AddressUse,
    ContactPointState,
    ContactPointSystem,
    ContactPointUse,
    PersonSex,
    TaxIDType,
)
from canvas_sdk.v1.data.utils import create_key


class Staff(Model):
    """Staff."""

    class Meta:
        db_table = "canvas_sdk_data_api_staff_001"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    id = models.CharField(
        max_length=32,
        db_column="key",
        unique=True,
        editable=False,
        default=create_key,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    prefix = models.CharField(max_length=100)
    suffix = models.CharField(max_length=100)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    maiden_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    previous_names = models.JSONField()
    birth_date = models.DateField(null=True)
    sex_at_birth = models.CharField(choices=PersonSex.choices, max_length=3)
    sexual_orientation_term = models.CharField(max_length=255)
    sexual_orientation_code = models.CharField(max_length=255)
    gender_identity_term = models.CharField(max_length=255)
    gender_identity_code = models.CharField(max_length=255)
    preferred_pronouns = models.CharField(max_length=255)
    biological_race_codes = ArrayField(models.CharField(max_length=100))
    biological_race_terms = ArrayField(models.CharField(max_length=255))
    cultural_ethnicity_codes = ArrayField(models.CharField(max_length=100))
    cultural_ethnicity_terms = ArrayField(models.CharField(max_length=255))
    last_known_timezone = TimeZoneField(null=True)
    active = models.BooleanField()
    primary_practice_location = models.ForeignKey(
        "v1.PracticeLocation", on_delete=models.DO_NOTHING, null=True
    )
    npi_number = models.CharField(max_length=10)
    nadean_number = models.CharField(max_length=20)
    group_npi_number = models.CharField(max_length=10)
    bill_through_organization = models.BooleanField()
    tax_id = models.CharField(max_length=25)
    tax_id_type = models.CharField(choices=TaxIDType.choices, max_length=1)
    spi_number = models.CharField(max_length=50)
    # TODO - uncomment when Language is developed
    # language = models.ForeignKey('v1.Language', on_delete=models.DO_NOTHING, related_name="staff_speakers", null=True)
    # language_secondary = models.ForeignKey('v1.Language', on_delete=models.DO_NOTHING, related_name="staff_secondary_speakers", null=True)
    personal_meeting_room_link = models.URLField(null=True)
    state = models.JSONField()
    user = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    schedule_column_ordering = models.IntegerField()
    default_supervising_provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="supervising_team", null=True
    )

    @property
    def photo_url(self) -> str:
        """Return the URL of the staff's first photo."""
        photo = self.photos.first()
        return photo.url if photo else "https://d3hn0m4rbsz438.cloudfront.net/avatar1.png"

    @cached_property
    def full_name(self) -> str:
        """Return Staff's first + last name."""
        return f"{self.first_name} {self.last_name}"

    @cached_property
    def top_clinical_role(self) -> "StaffRole | None":
        """Returns the topmost clinical role to assist in determining privilege levels.

        Returns:
            StaffRole | None: the topmost clinical role of the staff member.
        """
        roles = [
            role
            for role in self.roles.all()
            if role.domain in StaffRole.RoleDomain.clinical_domains()
        ]

        if not roles:
            return None

        return roles[0]

    @cached_property
    def top_role_abbreviation(self) -> str | None:
        """Returns the abbreviation string for the topmost role that the Staff object has.

        Returns:
            Optional[str]: The abbreviation for the topmost role, if available.
        """
        return self.top_clinical_role.public_abbreviation if self.top_clinical_role else None

    @cached_property
    def credentialed_name(self) -> str:
        """Returns the full name of the staff member, suffixed with their topmost credential.

        Returns:
            str: The credentialed full name of the staff member.
        """
        return " ".join(filter(bool, [self.full_name, self.top_role_abbreviation or ""]))


class StaffContactPoint(IdentifiableModel):
    """StaffContactPoint."""

    class Meta:
        db_table = "canvas_sdk_data_api_staffcontactpoint_001"

    system = models.CharField(choices=ContactPointSystem.choices, max_length=20)
    value = models.CharField(max_length=100)
    use = models.CharField(choices=ContactPointUse.choices, max_length=20)
    use_notes = models.CharField(max_length=255)
    rank = models.IntegerField()
    state = models.CharField(choices=ContactPointState.choices, max_length=20)
    staff = models.ForeignKey(Staff, on_delete=models.DO_NOTHING, related_name="telecom")


class StaffAddress(IdentifiableModel):
    """StaffAddress."""

    class Meta:
        db_table = "canvas_sdk_data_api_staffaddress_001"

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
    staff = models.ForeignKey(Staff, on_delete=models.DO_NOTHING, related_name="addresses")


class StaffPhoto(Model):
    """StaffPhoto."""

    class Meta:
        db_table = "canvas_sdk_data_api_staffphoto_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="photos")
    url = models.CharField(
        default="https://d3hn0m4rbsz438.cloudfront.net/avatar1.png", max_length=512
    )
    title = models.CharField(max_length=255, blank=True, default="")


class StaffRole(Model):
    """StaffRole."""

    class Meta:
        db_table = "canvas_sdk_data_api_staffrole_001"

    class RoleDomain(TextChoices):
        CLINICAL = "CLI", "Clinical"
        ADMINISTRATIVE = "ADM", "Administrative"
        HYBRID = "HYB", "Hybrid"

        @staticmethod
        def clinical_domains() -> list["StaffRole.RoleDomain"]:
            """Return a list of clinical role domains."""
            return [StaffRole.RoleDomain.CLINICAL, StaffRole.RoleDomain.HYBRID]

    class RoleType(TextChoices):
        NON_LICENSED = "NON-LICENSED", "Non-Licensed"
        LICENSED = "LICENSED", "Licensed"
        PROVIDER = "PROVIDER", "Provider"

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="roles")
    internal_code = models.CharField(max_length=10)
    public_abbreviation = models.CharField(max_length=10, default="", blank=True)
    domain = models.CharField(max_length=3, choices=RoleDomain.choices, db_index=True)
    name = models.CharField(max_length=50)
    domain_privilege_level = models.IntegerField(default=0)
    permissions = models.JSONField(default=dict, blank=True, null=True)
    role_type = models.CharField(max_length=50, choices=RoleType.choices, blank=True)


__exports__ = ("Staff", "StaffContactPoint", "StaffAddress", "StaffPhoto", "StaffRole")

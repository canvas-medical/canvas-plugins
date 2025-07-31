from functools import cached_property

from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class ServiceProvider(IdentifiableModel):
    """ServiceProvider."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_serviceprovider_001"

    first_name = models.CharField(max_length=512)
    # organizations won't have a last name
    last_name = models.CharField(max_length=512, default="", blank=True)
    business_fax = models.CharField(max_length=512, null=True, blank=True)
    business_phone = models.CharField(max_length=512, null=True, blank=True)
    business_address = models.CharField(max_length=512, null=True, blank=True)
    specialty = models.CharField(max_length=512)
    practice_name = models.CharField(max_length=512, null=True, blank=True)
    notes = models.TextField(default="", null=True, blank=True)

    @property
    def full_name(self) -> str:
        """Service provider full name."""
        return f"{self.first_name} {self.last_name}"

    @cached_property
    def full_name_and_specialty(self) -> str:
        """Service provider full name and specialty."""
        name_components: list[str] = []

        # Note 1: if firstName is (TBD) then insert at the end instead of the beginning
        if self.first_name != "(TBD)":
            name_components.append(self.first_name)

        if self.first_name != self.last_name:
            name_components.append(self.last_name)

        if self.practice_name and self.practice_name != "(TBD)":
            name_components.append(f"({self.practice_name}),")

        if self.specialty not in [self.first_name, self.last_name, self.practice_name]:
            name_components.append(self.specialty)

        # see Note 1
        if self.first_name == "(TBD)":
            name_components.append(self.first_name)

        return " ".join(name_components)


__exports__ = ("ServiceProvider",)

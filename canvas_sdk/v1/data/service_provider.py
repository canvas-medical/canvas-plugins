from functools import cached_property
from typing import Any

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
    is_active = models.BooleanField(default=True)
    npi = models.CharField(max_length=10, null=True, blank=True)
    direct_address = models.CharField(max_length=512, null=True, blank=True)
    # True only for providers a customer created through the SDK. Filter on it to search a
    # customer's own directory; everything else, including Science-derived providers, is False.
    is_customer_managed = models.BooleanField(default=False)

    # The shared directory contact this provider came from, null when it came from none. Read-only,
    # and not a provenance signal: legacy providers predate this tracking, so use
    # is_customer_managed to tell a customer's own providers apart.
    science_contact_id = models.IntegerField(null=True, blank=True)

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

    def as_search_result(self, annotations: list[str] | None = None) -> dict[str, Any]:
        """Shape this provider as an autocomplete result for a command's search."""
        description = " • ".join(
            part for part in (self.specialty, self.practice_name, self.business_address) if part
        )

        return {
            "text": self.full_name.strip(),
            "value": self.dbid,
            "description": description,
            "annotations": list(annotations or []),
            "extra": {
                # service_provider_id is load-bearing, so don't drop it: without it the write path
                # treats an "id" key as a Science contact id. No "id" is sent here either.
                "contact": {
                    "service_provider_id": self.dbid,
                    "science_contact_id": self.science_contact_id,
                    "firstName": self.first_name,
                    "lastName": self.last_name,
                    "businessFax": self.business_fax,
                    "businessPhone": self.business_phone,
                    "businessAddress": self.business_address,
                    "specialty": self.specialty,
                    "practiceName": self.practice_name,
                    "notes": self.notes,
                }
            },
        }

    def as_search_contact(self, annotations: list[str] | None = None) -> dict[str, Any]:
        """Shape this provider as a contact record for a contact directory search."""
        return {
            "id": self.dbid,
            "serviceProviderId": self.dbid,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "practiceName": self.practice_name,
            "specialty": self.specialty,
            "businessAddress": self.business_address,
            "businessPhone": self.business_phone,
            "businessFax": self.business_fax,
            "annotations": list(annotations or []),
        }


__exports__ = ("ServiceProvider",)

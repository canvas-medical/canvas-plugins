import unicodedata
from typing import Any

import arrow
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class EligibilityResponseStatus(models.TextChoices):
    """The eligibility check result derived from an EligibilityResponse."""

    ACTIVE = "Active", "Active"
    INACTIVE = "Inactive", "Inactive"
    FAILED = "Failed", "Failed"
    UNKNOWN = "Unknown", "Unknown"
    NOT_APPLICABLE = "NotApplicable", "Not Applicable"


class _NoMatchedPersonError(Exception):
    pass


class EligibilityRequest(TimestampedModel, IdentifiableModel):
    """A 270 coverage eligibility request sent to a payer."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_eligibilityrequest_001"

    coverage = models.ForeignKey(
        "v1.Coverage", on_delete=models.DO_NOTHING, related_name="requests", null=True
    )
    trading_partner_id = models.CharField(max_length=255)
    member = models.JSONField()
    provider = models.JSONField(null=True, blank=True)
    payload = models.TextField(default="")
    control_number = models.CharField(max_length=20, default="", blank=True)


class EligibilityResponse(TimestampedModel, IdentifiableModel):
    """A 271 coverage eligibility response and its derived check ``status``."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_eligibilityresponse_001"

    eligibility_request = models.ForeignKey(
        "v1.EligibilityRequest",
        on_delete=models.DO_NOTHING,
        related_name="eligibility_responses",
        null=True,
    )
    coverage = models.ForeignKey(
        "v1.Coverage", on_delete=models.DO_NOTHING, related_name="eligibility_responses"
    )
    client_id = models.CharField(max_length=100, blank=True, default="")
    correlation_id = models.CharField(max_length=100, blank=True, default="")
    deductible = models.JSONField()
    out_of_pocket = models.JSONField(null=True, blank=True)
    coverage_info = models.JSONField()
    payer = models.JSONField(null=True, blank=True)
    provider = models.JSONField(null=True, blank=True)
    service_type_codes = ArrayField(models.CharField(max_length=2, blank=True, default=""))
    service_types = ArrayField(models.CharField(max_length=100, blank=True, default=""))
    subscriber = models.JSONField(null=True, blank=True)
    trading_partner_id = models.CharField(max_length=100, blank=True, default="")
    valid_request = models.BooleanField()
    errors = ArrayField(models.TextField(), null=True, default=None)
    eligid = models.CharField(max_length=32, default="", blank=True)
    x12_response = models.TextField(default="", blank=True)
    parsed_x12_response = models.JSONField(default=dict, blank=True)

    # --- status derivation, ported from home-app quality_and_revenue.models.eligibility_request ---
    # (strict_unidecode -> stdlib unicodedata; django.contrib.admin flatten -> inline comprehension)

    @staticmethod
    def _normalize_name(name: str | None) -> str:
        stripped = (
            unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
        )
        return stripped.strip().lower().replace(" ", "")

    def _get_subscriber(self) -> dict | None:
        try:
            subscribers = self.parsed_x12_response["receivers"][0]["subscribers"]
        except (KeyError, TypeError, IndexError):
            return None
        return subscribers[0] if subscribers else None

    def _is_patient_match(self, parsed_person: dict[str, Any], patient: Any) -> bool:
        try:
            info = parsed_person["personal_information"]
            birth_date_matches = info["demographic_information"]["birth_date"] == arrow.get(
                patient.birth_date
            ).format("YYYY-MM-DD")
            last_name_matches = self._normalize_name(info["last_name"]) == self._normalize_name(
                patient.last_name
            )
            response_first = self._normalize_name(info.get("first_name"))
            patient_first = self._normalize_name(patient.first_name)
            first_name_matches = (
                not response_first
                or not patient_first
                or response_first.startswith(patient_first)
                or patient_first.startswith(response_first)
            )
            return birth_date_matches and last_name_matches and first_name_matches
        except (KeyError, TypeError, AttributeError):
            return False

    def _get_relevant_person(self) -> dict:
        try:
            coverage = self.coverage
        except ObjectDoesNotExist:
            raise _NoMatchedPersonError from None
        if coverage is None:
            raise _NoMatchedPersonError
        try:
            patient = coverage.patient
            subscriber = coverage.subscriber
            parsed_subscriber = self._get_subscriber()
            if not parsed_subscriber:
                raise _NoMatchedPersonError
            if patient == subscriber:
                if self._is_patient_match(parsed_subscriber, patient):
                    return parsed_subscriber
                raise _NoMatchedPersonError
            for dependent in parsed_subscriber["dependents"]:
                if self._is_patient_match(dependent, patient):
                    return dependent
        except (KeyError, TypeError, IndexError, AttributeError):
            pass
        raise _NoMatchedPersonError

    @property
    def eligibility_or_benefit_information(self) -> list:
        """Eligibility/benefit info for the person matching the coverage, else the subscriber's."""
        try:
            return self._get_relevant_person()["eligibility_or_benefit_information"]
        except _NoMatchedPersonError:
            subscriber = self._get_subscriber()
            if subscriber is None:
                return []
            try:
                return subscriber["eligibility_or_benefit_information"]
            except (KeyError, TypeError, IndexError, AttributeError):
                return []
        except (KeyError, TypeError, IndexError, AttributeError):
            return []

    @property
    def status(self) -> EligibilityResponseStatus:
        """FAILED when the check errored, INACTIVE when the payer reports an inactive section, else ACTIVE."""
        if self.errors:
            return EligibilityResponseStatus.FAILED

        eligible_service_types = (
            "Health Benefit Plan Coverage",
            "Professional (Physician) Visit - Office",
        )
        eligible_services = [
            info
            for service in self.eligibility_or_benefit_information
            if service.get("service_type") in eligible_service_types
            for info in service.get("info") or []
        ]

        if any("Inactive" in (info.get("information_type") or "") for info in eligible_services):
            return EligibilityResponseStatus.INACTIVE

        return EligibilityResponseStatus.ACTIVE


__exports__ = ("EligibilityRequest", "EligibilityResponse", "EligibilityResponseStatus")

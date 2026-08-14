import datetime
import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects.metadata import Metadata as PatientMetadata
from canvas_sdk.v1.data import ContactCategory, PracticeLocation, Staff
from canvas_sdk.v1.data import Patient as PatientModel
from canvas_sdk.v1.data.common import (
    AddressType,
    AddressUse,
    ContactPointSystem,
    ContactPointUse,
    PersonSex,
)
from canvas_sdk.v1.data.utils import create_key


@dataclass
class PatientContactPoint:
    """A class representing a patient contact point."""

    system: ContactPointSystem
    value: str
    use: ContactPointUse
    rank: int
    has_consent: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the contact point to a dictionary."""
        return {
            "system": self.system.value,
            "value": self.value,
            "use": self.use.value,
            "rank": self.rank,
            "has_consent": self.has_consent,
        }


@dataclass
class PatientContactCategory:
    """A relationship category for a patient contact (e.g. emergency contact, next-of-kin).

    All three fields are required and none is defaulted: the coding must already exist in the
    instance. Look one up with the `ContactCategory` data model rather than inventing a coding.
    """

    code: str
    code_system: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the contact category to a dictionary."""
        return {
            "code_system": self.code_system,
            "code": self.code,
            "name": self.name,
        }


@dataclass
class PatientContact:
    """A class representing a patient contact, such as an emergency contact or related person.

    Whether a contact is added or modified is decided by `contact_identifier`, not by which
    method the `Patient` effect was applied with: omit it to add a contact, supply it to target
    the contact it names. So `Patient(...).update()` can add a contact to a patient that already
    exists, which is the common case for a plugin populating contacts after intake.
    """

    name: str | None = None
    # Omit to add a contact. Supply it to update or remove the contact it names; on a create it
    # is the id the new contact is given.
    contact_identifier: str | uuid.UUID | None = None
    phone_number: str | None = None
    email: str | None = None
    comments: str | None = None
    categories: list[PatientContactCategory] | None = None
    # Set instead of `name` to point the contact at an existing Canvas patient.
    related_patient: str | uuid.UUID | None = None
    # Set with `contact_identifier` to remove an existing contact rather than create or update one.
    inactive: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the contact to a dictionary, omitting any field that was not set.

        Unset fields are omitted rather than sent as null: the write path derives the columns
        to update from the keys it receives and reads null as an empty value, so sending every
        key would make an update of one field blank all the others. Pass "" to clear a value.
        """
        values: dict[str, Any] = {
            key: value
            for key, value in (
                ("name", self.name),
                ("phone_number", self.phone_number),
                ("email", self.email),
                ("comments", self.comments),
                ("inactive", self.inactive),
            )
            if value is not None
        }

        if self.contact_identifier is not None:
            # A contact's id is a real UUID column, so either form of the same UUID resolves.
            values["contact_identifier"] = str(self.contact_identifier)

        if self.related_patient is not None:
            values["related_patient"] = _as_patient_key(self.related_patient)

        if self.categories is not None:
            values["categories"] = [category.to_dict() for category in self.categories]

        return values


@dataclass
class PatientExternalIdentifier:
    """A class representing a patient external identifier."""

    value: str
    system: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the external identifier to a dictionary."""
        return {
            "system": self.system,
            "value": self.value,
        }


@dataclass
class PatientPreferredPharmacy:
    """A class representing a preferred pharmacy."""

    ncpdp_id: str
    default: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert the preferred pharmacy to a dictionary."""
        return {
            "ncpdp_id": self.ncpdp_id,
            "default": self.default,
        }


@dataclass
class PatientAddress:
    """A class representing a patient address."""

    line1: str
    country: str
    line2: str | None = None
    use: AddressUse = AddressUse.HOME
    type: AddressType = AddressType.BOTH
    city: str | None = None
    district: str | None = None
    state_code: str | None = None
    postal_code: str | None = None
    longitude: float | None = None
    latitude: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the address to a dictionary."""
        return {
            "line1": self.line1,
            "line2": self.line2,
            "country": self.country,
            "use": self.use.value,
            "type": self.type.value,
            "city": self.city,
            "district": self.district,
            "state_code": self.state_code,
            "postal_code": self.postal_code,
            "longitude": self.longitude,
            "latitude": self.latitude,
        }


_PATIENT_ID_RE = re.compile(r"\A[0-9a-f]{32}\Z")
# The contact phone number column holds exactly 10 digits, matching the UI's own validation.
_CONTACT_PHONE_RE = re.compile(r"\A[0-9]{10}\Z")
_EMAIL_RE = re.compile(r"\A[^@\s]+@[^@\s]+\.[^@\s]+\Z")


def generate_patient_id() -> str:
    """Generate a patient id (a UUID4 hex string without hyphens) for Patient(patient_id=...)."""
    return create_key()


def _is_valid_patient_id(value: str) -> bool:
    """Return True if value is a well-formed patient id (32-character lowercase hex)."""
    return bool(_PATIENT_ID_RE.match(value))


def _is_valid_uuid(value: str | uuid.UUID) -> bool:
    """Return True if value is a well-formed UUID, hyphenated or not."""
    if isinstance(value, uuid.UUID):
        return True
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def _as_patient_key(value: str | uuid.UUID) -> str:
    """Normalize a patient reference to the 32-character hex form stored as a patient's key.

    A uuid.UUID object and the hyphenated string name the same patient as the bare hex, but the
    column holds hex and the lookup does not normalize, so an un-normalized value would come
    back as a patient that does not exist. A value that is not a UUID at all is passed through
    for the validator to reject with a message about the real problem.
    """
    try:
        return uuid.UUID(str(value)).hex
    except (ValueError, AttributeError, TypeError):
        return str(value)


class Patient(TrackableFieldsModel):
    """Effect to create a Patient record."""

    class Meta:
        effect_type = "PATIENT"

    patient_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    birthdate: datetime.date | None = None
    prefix: str | None = None
    suffix: str | None = None
    sex_at_birth: PersonSex | None = None
    nickname: str | None = None
    social_security_number: str | None = None
    administrative_note: str | None = None
    clinical_note: str | None = None
    default_location_id: str | None = None
    default_provider_id: str | None = None
    active: bool | None = None
    deceased: bool | None = None
    deceased_datetime: datetime.datetime | None = None
    deceased_cause: str | None = None
    deceased_comment: str | None = None
    biological_race_codes: list[str] | None = None
    cultural_ethnicity_codes: list[str] | None = None
    previous_names: list[str] | None = None
    contact_points: list[PatientContactPoint] | None = None
    contacts: list[PatientContact] | None = None
    external_identifiers: list[PatientExternalIdentifier] | None = None
    preferred_pharmacies: list[PatientPreferredPharmacy] | None = None
    addresses: list[PatientAddress] | None = None
    metadata: list[PatientMetadata] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the patient as a dictionary."""
        values = super().values

        if self.is_dirty("contact_points"):
            values["contact_points"] = (
                [cp.to_dict() for cp in self.contact_points]
                if self.contact_points is not None
                else None
            )

        if self.is_dirty("contacts"):
            values["contacts"] = (
                [contact.to_dict() for contact in self.contacts]
                if self.contacts is not None
                else None
            )

        if self.is_dirty("external_identifiers"):
            values["external_identifiers"] = (
                [ids.to_dict() for ids in self.external_identifiers]
                if self.external_identifiers is not None
                else None
            )

        if self.is_dirty("addresses"):
            values["addresses"] = (
                [addr.to_dict() for addr in self.addresses] if self.addresses is not None else None
            )

        if self.is_dirty("preferred_pharmacies"):
            values["preferred_pharmacies"] = (
                [pharmacy.to_dict() for pharmacy in self.preferred_pharmacies]
                if self.preferred_pharmacies
                else None
            )

        if self.is_dirty("metadata"):
            values["metadata"] = (
                [md.to_dict() for md in self.metadata] if self.metadata is not None else None
            )

        return values

    def _get_contact_error_details(self) -> list[InitErrorDetails]:
        """Validate each contact's shape, and its categories against the instance's codings.

        `contact_identifier` is what distinguishes an update of an existing contact from a new
        one, on `create` and `update` alike: supplying it targets that contact, omitting it adds
        a contact. So it is never required except to remove one, where there is nothing else to
        say which contact is meant.

        Existence of `related_patient` and of the contact behind `contact_identifier` is
        deliberately not checked here: effects are applied after the plugin returns, so a
        patient or contact created by an earlier effect in the same run does not exist yet at
        this point. Format is checked here, existence when the effect is applied. Category
        codings are instance reference data that no effect creates, so those are checked here.
        """
        errors: list[InitErrorDetails] = []
        codings: set[tuple[str, str]] = set()

        def error(message: str, value: Any) -> None:
            errors.append(self._create_error_detail("value", message, value))

        for contact in self.contacts or []:
            if contact.inactive:
                # A removal only needs the identifier of the contact to remove; requiring a
                # name or related_patient too would force a meaningless value onto a delete.
                if contact.contact_identifier is None:
                    error(
                        "'contact_identifier' is required to remove a contact via inactive=True.",
                        None,
                    )
            elif contact.name is None and contact.related_patient is None:
                error(
                    "A patient contact requires either 'name' (an inline person) or "
                    "'related_patient' (the key of an existing Canvas patient).",
                    None,
                )
            for field, value in (
                ("contact_identifier", contact.contact_identifier),
                ("related_patient", contact.related_patient),
            ):
                if value is not None and not _is_valid_uuid(value):
                    error(f"Contact '{field}' must be a UUID, got {value}.", value)
            # An empty string is how a builder clears a stored value, so only validate content.
            if contact.phone_number and not _CONTACT_PHONE_RE.match(contact.phone_number):
                error(
                    f"Contact 'phone_number' must be 10 digits, got {contact.phone_number}.",
                    contact.phone_number,
                )
            if contact.email and not _EMAIL_RE.match(contact.email):
                error(
                    f"Contact 'email' must be a valid email address, got {contact.email}.",
                    contact.email,
                )
            for category in contact.categories or []:
                if missing := [
                    field
                    for field in ("code", "code_system", "name")
                    if not getattr(category, field)
                ]:
                    error(
                        f"A contact category requires 'code', 'code_system' and 'name'; missing "
                        f"or blank: {', '.join(missing)}.",
                        None,
                    )
                else:
                    codings.add((category.code, category.code_system))

        if codings:
            # Resolved in one query rather than one per category.
            existing = set(
                ContactCategory.objects.filter(code__in={code for code, _ in codings}).values_list(
                    "code", "system"
                )
            )
            for code, code_system in sorted(codings - existing):
                error(
                    f"Contact category '{code}' (system '{code_system}') does not exist in this "
                    f"instance. Look up an existing coding with ContactCategory.objects.",
                    code,
                )

        return errors

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        errors.extend(self._get_contact_error_details())

        # Validate create-specific requirements
        if method == "create":
            if self.patient_id is not None and not _is_valid_patient_id(self.patient_id):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Patient ID must be a 32-character hex string (a UUID4 without "
                        "hyphens); use generate_patient_id() to generate one.",
                        self.patient_id,
                    )
                )

            # first_name and last_name are required for create
            if not self.first_name:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "First name is required when creating a new patient.",
                        self.first_name,
                    )
                )

            if not self.last_name:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Last name is required when creating a new patient.",
                        self.last_name,
                    )
                )

        # Validate update-specific requirements
        if method == "update":
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Patient ID must be set when updating an existing patient.",
                        self.patient_id,
                    )
                )
            elif not PatientModel.objects.filter(id=self.patient_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Patient with ID {self.patient_id} does not exist.",
                        self.patient_id,
                    )
                )

        if (
            self.default_location_id
            and not PracticeLocation.objects.filter(id=self.default_location_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Practice location with ID {self.default_location_id} does not exist.",
                    self.default_location_id,
                )
            )

        if (
            self.default_provider_id
            and not Staff.objects.filter(id=self.default_provider_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Provider with ID {self.default_provider_id} does not exist.",
                    self.default_provider_id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new Patient."""
        self._validate_before_effect("create")

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )

    def update(self) -> Effect:
        """Update an existing Patient."""
        self._validate_before_effect("update")

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = (
    "Patient",
    "PatientAddress",
    "PatientContact",
    "PatientContactCategory",
    "PatientContactPoint",
    "PatientExternalIdentifier",
    "PatientMetadata",
    "PatientPreferredPharmacy",
    "generate_patient_id",
)

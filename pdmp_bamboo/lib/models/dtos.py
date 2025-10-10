"""
Data Transfer Objects for PDMP data.

DTOs are immutable dataclasses that ensure data integrity.
"""

import re
from dataclasses import asdict, dataclass, field


class SexCode:
    """Standard sex/gender codes for PDMP data."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"


@dataclass(frozen=True)
class AddressDTO:
    """Data Transfer Object for Address data."""

    street: str = ""
    street2: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    zip_plus_four: str = ""

    def __post_init__(self):
        """Validate address data on construction."""
        # Validate ZIP code format if provided
        if self.zip_code and not re.match(r"^\d{5}$", self.zip_code):
            object.__setattr__(self, 'zip_code', self.zip_code)  # Allow for now, validation happens in validator

        # Validate state code if provided
        if self.state and len(self.state) not in (0, 2):
            object.__setattr__(self, 'state', self.state)  # Allow for now, validation happens in validator

    def is_empty(self) -> bool:
        """Check if address has any meaningful data."""
        return not any([self.street, self.street2, self.city, self.state, self.zip_code])

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility."""
        return asdict(self)


@dataclass(frozen=True)
class PatientDTO:
    """Data Transfer Object for Patient data."""

    id: str = ""
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    birth_date: str = ""
    sex: str = SexCode.UNKNOWN
    mrn: str = ""
    ssn: str = ""
    phone: str = ""
    address: AddressDTO = field(default_factory=AddressDTO)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = asdict(self)
        # Ensure address is dict (asdict handles nested dataclasses)
        return result


@dataclass(frozen=True)
class PractitionerDTO:
    """Data Transfer Object for Practitioner data."""

    id: str = ""
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    npi_number: str = ""
    dea_number: str = ""
    role: str = ""
    phone: str = ""
    email: str = ""
    active: bool = True
    license_number: str = ""
    license_type: str = ""
    license_state: str = ""
    organization_id: str = ""
    organization_name: str = ""
    practice_location_id: str = ""
    practice_location_name: str = ""
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class PracticeLocationDTO:
    """Data Transfer Object for Practice Location data."""

    id: str = ""
    name: str = ""
    npi: str = ""
    dea: str = ""
    ncpdp: str = ""
    phone: str = ""
    active: bool = True
    address: AddressDTO = field(default_factory=AddressDTO)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class OrganizationDTO:
    """Data Transfer Object for Organization data."""

    id: str = ""
    name: str = ""
    active: bool = True
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

class SexCode:
    """Standard sex/gender codes for PDMP data."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"


class AddressDTO:
    """Data Transfer Object for Address data."""

    def __init__(self, street="", street2="", city="", state="", zip_code="", zip_plus_four=""):
        self.street = street
        self.street2 = street2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.zip_plus_four = zip_plus_four

    def is_empty(self) -> bool:
        """Check if address has any meaningful data."""
        return not any([self.street, self.street2, self.city, self.state, self.zip_code])

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility."""
        return {
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "zip_plus_four": self.zip_plus_four,
        }


class PatientDTO:
    """Data Transfer Object for Patient data."""

    def __init__(
        self,
        id="",
        first_name="",
        last_name="",
        middle_name="",
        birth_date="",
        sex=SexCode.UNKNOWN,
        mrn="",
        ssn="",
        phone="",
        address=None,
        errors=None,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.birth_date = birth_date
        self.sex = sex
        self.mrn = mrn
        self.ssn = ssn
        self.phone = phone
        self.address = address or AddressDTO()
        self.errors = errors or []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "birth_date": self.birth_date,
            "sex": self.sex,
            "mrn": self.mrn,
            "ssn": self.ssn,
            "phone": self.phone,
            "address": self.address.to_dict() if self.address else {},
            "errors": self.errors,
        }


class PractitionerDTO:
    """Data Transfer Object for Practitioner data."""

    def __init__(
        self,
        id="",
        first_name="",
        last_name="",
        middle_name="",
        npi_number="",
        dea_number="",
        role="",
        phone="",
        email="",
        active=True,
        license_number="",
        license_type="",
        license_state="",
        organization_id="",
        organization_name="",
        practice_location_id="",
        practice_location_name="",
        errors=None,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.npi_number = npi_number
        self.dea_number = dea_number
        self.role = role
        self.phone = phone
        self.email = email
        self.active = active
        self.license_number = license_number
        self.license_type = license_type
        self.license_state = license_state
        self.organization_id = organization_id
        self.organization_name = organization_name
        self.practice_location_id = practice_location_id
        self.practice_location_name = practice_location_name
        self.errors = errors or []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "npi_number": self.npi_number,
            "dea_number": self.dea_number,
            "role": self.role,
            "phone": self.phone,
            "email": self.email,
            "active": self.active,
            "license_number": self.license_number,
            "license_type": self.license_type,
            "license_state": self.license_state,
            "organization_id": self.organization_id,
            "organization_name": self.organization_name,
            "practice_location_id": self.practice_location_id,
            "practice_location_name": self.practice_location_name,
            "errors": self.errors,
        }


class PracticeLocationDTO:
    """Data Transfer Object for Practice Location data."""

    def __init__(
        self,
        id="",
        name="",
        npi="",
        dea="",
        ncpdp="",
        phone="",
        active=True,
        address=None,
        errors=None,
    ):
        self.id = id
        self.name = name
        self.npi = npi
        self.dea = dea
        self.ncpdp = ncpdp
        self.phone = phone
        self.active = active
        self.address = address or AddressDTO()
        self.errors = errors or []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "npi": self.npi,
            "dea": self.dea,
            "ncpdp": self.ncpdp,
            "phone": self.phone,
            "active": self.active,
            "address": self.address.to_dict() if self.address else {},
            "errors": self.errors,
        }


class OrganizationDTO:
    """Data Transfer Object for Organization data."""

    def __init__(self, id="", name="", active=True, errors=None):
        self.id = id
        self.name = name
        self.active = active
        self.errors = errors or []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "errors": self.errors,
        }

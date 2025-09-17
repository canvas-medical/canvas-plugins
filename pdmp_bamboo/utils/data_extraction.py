from typing import List, Optional, Tuple
from canvas_sdk.v1.data import Patient


class SexCode:
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

    def __init__(self, id="", first_name="", last_name="", middle_name="", birth_date="",
                 sex=SexCode.UNKNOWN, mrn="", ssn="", phone="", address=None, errors=None):
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


class PatientMapper:
    """Maps Canvas Patient model to PatientDTO."""

    @staticmethod
    def extract_phone(patient: Patient) -> str:
        """Extract primary phone number from patient."""
        try:
            primary_phone = patient.primary_phone_number
            return primary_phone.value if primary_phone else ""
        except Exception:
            return ""

    @staticmethod
    def extract_address(patient: Patient) -> AddressDTO:
        """Extract address from patient addresses relationship."""
        try:
            addresses = patient.addresses.all()
            if addresses.exists():
                address = addresses.first()
                return AddressDTO(
                    street=address.line1 or "",
                    street2=address.line2 or "",
                    city=address.city or "",
                    state=address.state_code or "",
                    zip_code=address.postal_code or "",
                    zip_plus_four=""
                )
        except Exception:
            pass

        return AddressDTO()

    @staticmethod
    def normalize_sex_code(sex_at_birth: str) -> str:
        """Normalize sex code to standard values."""
        if not sex_at_birth:
            return SexCode.UNKNOWN

        sex_upper = sex_at_birth.upper()
        if sex_upper in ["UNK", "UNKNOWN", "U"]:
            return SexCode.UNKNOWN
        elif sex_upper in ["MALE", "M"]:
            return SexCode.MALE
        elif sex_upper in ["FEMALE", "F"]:
            return SexCode.FEMALE
        else:
            return SexCode.UNKNOWN

    @classmethod
    def map_to_dto(cls, patient: Patient) -> PatientDTO:
        """Map Patient model to PatientDTO."""
        phone = cls.extract_phone(patient)
        address = cls.extract_address(patient)
        sex = cls.normalize_sex_code(patient.sex_at_birth)

        return PatientDTO(
            id=patient.id,
            first_name=patient.first_name or "",
            last_name=patient.last_name or "",
            middle_name=patient.middle_name or "",
            birth_date=cls._format_birth_date(patient),
            sex=sex,
            mrn=patient.mrn or "",
            ssn=patient.social_security_number or "",
            phone=phone,
            address=address,
            errors=[]
        )

    @staticmethod
    def _format_birth_date(patient: Patient) -> str:
        """Format birth date for PDMP."""
        if patient.birth_date:
            return patient.birth_date.strftime("%Y-%m-%d")
        return ""


class PatientValidator:
    """Validates PatientDTO data."""

    def validate(self, patient: PatientDTO) -> List[str]:
        """Validate patient data and return list of errors."""
        errors = []

        # Required fields
        if not patient.first_name:
            errors.append("❌ Patient first name is REQUIRED")
        if not patient.last_name:
            errors.append("❌ Patient last name is REQUIRED")
        if not patient.birth_date:
            errors.append("❌ Patient birth date is REQUIRED")
        if patient.sex == SexCode.UNKNOWN:
            errors.append("❌ Patient sex/gender is REQUIRED")

        # Optional but recommended fields
        if patient.address.is_empty():
            errors.append("⚠️ WARNING: Patient address is missing")
        if not patient.phone:
            errors.append("⚠️ WARNING: Patient phone number is missing")
        if not patient.ssn:
            errors.append("⚠️ WARNING: Patient SSN is missing")

        return errors


class DataExtractionService:
    """Service for extracting and validating data from Canvas models."""

    def __init__(self):
        self.patient_mapper = PatientMapper()
        self.patient_validator = PatientValidator()

    def extract_patient(self, patient_id: str) -> Tuple[Optional[PatientDTO], list]:
        """Extract and validate patient data."""
        try:
            patient = Patient.objects.get(id=patient_id)
            patient_dto = self.patient_mapper.map_to_dto(patient)
            validation_errors = self.patient_validator.validate(patient_dto)
            patient_dto.errors = validation_errors

            return patient_dto, validation_errors

        except Patient.DoesNotExist:
            return None, [f"Patient with ID '{patient_id}' not found"]
        except Exception as e:
            return None, [f"Error retrieving patient data: {str(e)}"]
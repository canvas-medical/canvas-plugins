from canvas_sdk.v1.data import Patient
from pdmp_bamboo.models.dtos import AddressDTO, SexCode, PatientDTO

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
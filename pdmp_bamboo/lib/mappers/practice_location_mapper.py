from canvas_sdk.v1.data import PracticeLocation
from logger import log
from pdmp_bamboo.lib.models.dtos import AddressDTO, PracticeLocationDTO
from pdmp_bamboo.lib.utils.common import safe_get_attr


class PracticeLocationMapper:
    """Maps Canvas PracticeLocation model to PracticeLocationDTO."""

    @staticmethod
    def extract_address(practice_location: PracticeLocation) -> AddressDTO:
        """Extract address from practice location addresses relationship."""
        try:
            addresses = practice_location.addresses.all()
            if addresses.exists():
                address = addresses.first()
                log.info(f"PracticeLocationMapper: Found address: {address}")

                return AddressDTO(
                    street=address.line1 or "",
                    street2=address.line2 or "",
                    city=address.city or "",
                    state=address.state_code or "",
                    zip_code=address.postal_code or "",
                    zip_plus_four="",
                )
        except Exception as e:
            log.info(f"PracticeLocationMapper: Could not extract address: {e}")

        return AddressDTO()  # Empty address

    @classmethod
    def map_to_dto(cls, practice_location: PracticeLocation) -> PracticeLocationDTO:
        """Map PracticeLocation model to PracticeLocationDTO."""
        address = cls.extract_address(practice_location)

        return PracticeLocationDTO(
            id=str(practice_location.id),
            name=practice_location.full_name or "",
            npi=practice_location.npi_number or "",
            dea="",  # DEA numbers belong to practitioners, not practice locations
            # ncpdp=practice_location.ncpdp or "", not available
            # phone=practice_location.phone or "", not available
            active=practice_location.active,
            address=address,
            errors=[],
        )

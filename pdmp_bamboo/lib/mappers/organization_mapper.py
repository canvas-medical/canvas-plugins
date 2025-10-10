from canvas_sdk.v1.data import Organization, PracticeLocation
from logger import log
from pdmp_bamboo.lib.models.dtos import OrganizationDTO
from pdmp_bamboo.lib.utils.common import safe_get_attr


class OrganizationMapper:
    """Maps Canvas Organization model to OrganizationDTO."""

    @classmethod
    def map_to_dto(
        cls, organization: Organization, practice_location: PracticeLocation
    ) -> OrganizationDTO:
        """Map Organization to OrganizationDTO."""
        organization_dto = OrganizationDTO(
            id=str(organization.dbid),
            name=organization.full_name or organization.short_name or "",
            active=getattr(organization, "active", True),
        )

        log.info(f"OrganizationMapper: Organization DTO created")
        return organization_dto

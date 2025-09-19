from canvas_sdk.v1.data import Organization, PracticeLocation
from pdmp_bamboo.models.dtos import OrganizationDTO
from logger import log


def _safe_get_attr(obj, attr_name, default=None):
    """Safely get attribute from object, return default if not found."""
    try:
        return getattr(obj, attr_name, default)
    except (AttributeError, TypeError):
        return default


class OrganizationMapper:
    """Maps Canvas Organization model to OrganizationDTO."""

    @classmethod
    def map_to_dto(cls, organization: Organization, practice_location: PracticeLocation) -> OrganizationDTO:
        """Map Organization to OrganizationDTO."""
        organization_dto = OrganizationDTO(
            id=str(organization.dbid),
            name=organization.full_name or organization.short_name or "",
            active=getattr(organization, 'active', True),
            errors=[]
        )

        log.info(f"OrganizationMapper: Organization DTO created: {organization_dto.__dict__}")
        return organization_dto
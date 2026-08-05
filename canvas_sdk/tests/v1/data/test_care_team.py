import pytest

from canvas_sdk.test_utils.factories import (
    OrganizationalEntityFactory,
    PatientFactory,
    ServiceProviderFactory,
)
from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus
from canvas_sdk.v1.data.organizational_entity import OrganizationalEntity


@pytest.mark.django_db
def test_external_member_resolves_to_service_provider_and_fax() -> None:
    """An external care team membership exposes its ServiceProvider and fax in-process."""
    service_provider = ServiceProviderFactory.create(business_fax="18005551234")
    content_type = ContentTypeFactory.create(app_label="data_integration", model="serviceprovider")
    entity = OrganizationalEntityFactory.create(
        content_type=content_type,
        object_id=service_provider.dbid,
        type=OrganizationalEntity.OrganizationalEntityType.SERVICE_PROVIDER,
    )
    membership = CareTeamMembership.objects.create(
        patient=PatientFactory.create(),
        staff=None,
        organizational_entity=entity,
        status=CareTeamMembershipStatus.ACTIVE,
        lead=False,
        role_code="",
        role_system="",
        role_display="",
    )

    assert membership.service_provider is not None
    assert membership.service_provider.dbid == service_provider.dbid
    assert membership.service_provider.business_fax == "18005551234"


@pytest.mark.django_db
def test_internal_member_has_no_service_provider() -> None:
    """A staff-backed (internal) membership has no organizational entity or service provider."""
    membership = CareTeamMembership.objects.create(
        patient=PatientFactory.create(),
        status=CareTeamMembershipStatus.ACTIVE,
        lead=False,
        role_code="",
        role_system="",
        role_display="",
    )

    assert membership.organizational_entity is None
    assert membership.service_provider is None


@pytest.mark.django_db
def test_non_service_provider_entity_returns_none() -> None:
    """A non-ServiceProvider organizational entity does not resolve to a service provider."""
    entity = OrganizationalEntityFactory.create(
        type=OrganizationalEntity.OrganizationalEntityType.VENDOR,
    )

    assert entity.service_provider is None


@pytest.mark.django_db
def test_filter_memberships_by_service_provider() -> None:
    """A plugin can reverse-look-up every membership linked to a specific ServiceProvider."""
    content_type = ContentTypeFactory.create(app_label="data_integration", model="serviceprovider")
    provider = ServiceProviderFactory.create()
    other_provider = ServiceProviderFactory.create()

    common = {
        "status": CareTeamMembershipStatus.ACTIVE,
        "lead": False,
        "role_code": "",
        "role_system": "",
        "role_display": "",
    }
    match_a = CareTeamMembership.objects.create(
        patient=PatientFactory.create(),
        staff=None,
        organizational_entity=OrganizationalEntityFactory.create(
            content_type=content_type,
            object_id=provider.dbid,
            type=OrganizationalEntity.OrganizationalEntityType.SERVICE_PROVIDER,
        ),
        **common,
    )
    match_b = CareTeamMembership.objects.create(
        patient=PatientFactory.create(),
        staff=None,
        organizational_entity=OrganizationalEntityFactory.create(
            content_type=content_type,
            object_id=provider.dbid,
            type=OrganizationalEntity.OrganizationalEntityType.SERVICE_PROVIDER,
        ),
        **common,
    )
    # A membership to a different provider -- must be excluded by object_id.
    CareTeamMembership.objects.create(
        patient=PatientFactory.create(),
        staff=None,
        organizational_entity=OrganizationalEntityFactory.create(
            content_type=content_type,
            object_id=other_provider.dbid,
            type=OrganizationalEntity.OrganizationalEntityType.SERVICE_PROVIDER,
        ),
        **common,
    )
    # An internal (staff-backed) membership with no entity -- must be excluded.
    CareTeamMembership.objects.create(patient=PatientFactory.create(), **common)

    matches = CareTeamMembership.objects.filter(
        organizational_entity__content_type__model="serviceprovider",
        organizational_entity__object_id=provider.dbid,
    )

    assert set(matches.values_list("dbid", flat=True)) == {match_a.dbid, match_b.dbid}

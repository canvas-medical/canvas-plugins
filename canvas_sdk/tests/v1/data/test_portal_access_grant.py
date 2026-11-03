import datetime

import pytest
from django.db import models

from canvas_sdk.handlers.simple_api import PortalAccess, PortalAccessLevel
from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    PatientFactory,
    PortalAccessGrantFactory,
)
from canvas_sdk.v1.data import PortalAccessGrant


@pytest.mark.django_db
def test_a_login_reads_each_chart_it_was_given_and_its_access() -> None:
    """A login's grants name the charts it was given, with the level it has in each area."""
    representative = CanvasUserFactory.create()
    maya = PatientFactory.create()
    leo = PatientFactory.create()
    to_maya = PortalAccessGrantFactory.create(
        user=representative, patient=maya, clinical="none", billing="view"
    )
    to_leo = PortalAccessGrantFactory.create(user=representative, patient=leo)
    PortalAccessGrantFactory.create(patient=maya)

    assert set(representative.portal_grants.all()) == {to_maya, to_leo}

    grant = PortalAccessGrant.objects.get(user=representative, patient=maya)
    assert [grant.appointments, grant.messaging, grant.clinical, grant.billing] == [
        "act",
        "act",
        "none",
        "view",
    ]
    assert not PortalAccessLevel(grant.clinical)
    assert PortalAccessLevel(grant.billing) < PortalAccessLevel.ACT


@pytest.mark.django_db
def test_a_chart_names_who_it_was_given_to_and_keeps_ended_access_as_history() -> None:
    """A chart's grants include revoked and flagged ones, which no longer give the chart."""
    maya = PatientFactory.create()
    now = datetime.datetime.now(datetime.UTC)
    giving = PortalAccessGrantFactory.create(patient=maya, contact_relationship="Father")
    PortalAccessGrantFactory.create(patient=maya, revoked_at=now, revoke_reason="Custody changed")
    PortalAccessGrantFactory.create(patient=maya, flagged_at=now)

    assert maya.portal_grants.count() == 3
    assert list(maya.portal_grants.filter(revoked_at__isnull=True, flagged_at__isnull=True)) == [
        giving
    ]
    assert giving.contact_relationship == "Father"


@pytest.mark.django_db
def test_a_grant_is_dated_when_it_is_created_whatever_date_is_passed() -> None:
    """granted_at is set when the grant is created, so a date passed in is ignored."""
    long_ago = datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC)
    before = datetime.datetime.now(datetime.UTC)

    grant = PortalAccessGrantFactory.create(granted_at=long_ago)

    assert grant.granted_at >= before


def test_each_area_takes_a_portal_access_level_and_allows_act_unless_limited() -> None:
    """Each area's level is one of PortalAccessLevel's choices, act unless staff limited it."""
    grant = PortalAccessGrant()

    for area in PortalAccess.AREAS:
        field = PortalAccessGrant._meta.get_field(area)
        assert isinstance(field, models.CharField) and field.choices == PortalAccessLevel.choices
        assert getattr(grant, area) == PortalAccessLevel.ACT


def test_reads_the_portal_access_grant_view() -> None:
    """The model is backed by the versioned view over home-app's portal access grants."""
    assert PortalAccessGrant._meta.db_table == "canvas_sdk_data_api_portalaccessgrant_001"

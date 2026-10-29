import datetime

import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, PortalInvitationFactory
from canvas_sdk.v1.data import (
    CanvasUser,
    PortalInvitation,
    PortalInvitationRejectionReason,
    PortalInvitationStatus,
)


@pytest.mark.django_db
def test_a_users_invitations_resolve_from_the_user() -> None:
    """A user's invitations resolve from CanvasUser and exclude other users' invitations."""
    user = CanvasUserFactory.create()
    invitation = PortalInvitationFactory.create(user=user)
    PortalInvitationFactory.create()

    assert list(user.portal_invitations.all()) == [invitation]


@pytest.mark.django_db
def test_invitations_filter_by_status() -> None:
    """A worklist can separate expired-and-never-opened links from expired-after-an-open links."""
    now = datetime.datetime.now(datetime.UTC)
    unopened = PortalInvitationFactory.create(status=PortalInvitationStatus.EXPIRED)
    PortalInvitationFactory.create(status=PortalInvitationStatus.EXPIRED, first_opened_at=now)
    PortalInvitationFactory.create(status=PortalInvitationStatus.CLAIMED, claimed_at=now)

    expired_unopened = PortalInvitation.objects.filter(
        status=PortalInvitationStatus.EXPIRED, first_opened_at__isnull=True
    )

    assert list(expired_unopened) == [unopened]


@pytest.mark.django_db
def test_a_rejected_click_keeps_its_reason() -> None:
    """A rejected click records when it happened and why."""
    now = datetime.datetime.now(datetime.UTC)
    invitation = PortalInvitationFactory.create(
        last_rejected_at=now,
        last_rejection_reason=PortalInvitationRejectionReason.DIFFERENT_ACCOUNT,
    )

    stored = PortalInvitation.objects.get(id=invitation.id)

    assert stored.last_rejected_at == now
    assert stored.last_rejection_reason == "different_account"
    assert stored.is_redeemable is True


@pytest.mark.django_db
def test_last_login_reads_through_the_user() -> None:
    """A user's last login can be read through the SDK."""
    logged_in_at = datetime.datetime(2026, 10, 1, 12, 0, tzinfo=datetime.UTC)
    user = CanvasUserFactory.create(last_login=logged_in_at)

    assert CanvasUser.objects.get(dbid=user.dbid).last_login == logged_in_at

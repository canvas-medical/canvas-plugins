import datetime

import factory

from canvas_sdk.v1.data import PortalInvitation, PortalInvitationStatus


class PortalInvitationFactory(factory.django.DjangoModelFactory[PortalInvitation]):
    """Factory for creating a PortalInvitation."""

    class Meta:
        model = PortalInvitation

    user = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    expires_at = factory.LazyFunction(
        lambda: datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    )
    status = PortalInvitationStatus.PENDING
    is_redeemable = True

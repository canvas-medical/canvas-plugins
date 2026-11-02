import datetime

import factory

from canvas_sdk.v1.data import PortalAccessGrant


class PortalAccessGrantFactory(factory.django.DjangoModelFactory[PortalAccessGrant]):
    """Factory for creating a PortalAccessGrant with full access and a confirmed date of birth."""

    class Meta:
        model = PortalAccessGrant

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    user = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    contact_name = factory.Faker("name")
    contact_relationship = "Mother"
    appointments = "act"
    messaging = "act"
    clinical = "act"
    billing = "act"
    dob_verified_at = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC))
    granted_by = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    granted_at = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC))

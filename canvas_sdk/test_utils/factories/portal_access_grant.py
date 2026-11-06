import datetime

import factory

from canvas_sdk.v1.data import PortalAccessGrant, PortalAccessLevel


class PortalAccessGrantFactory(factory.django.DjangoModelFactory[PortalAccessGrant]):
    """Factory for creating a PortalAccessGrant from one of the patient's contacts, with full access
    and a confirmed date of birth.
    """

    class Meta:
        model = PortalAccessGrant

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    user = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    contact = factory.SubFactory(
        "canvas_sdk.test_utils.factories.PatientContactPersonFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    contact_name = factory.SelfAttribute("contact.name")
    contact_relationship = "Mother"
    appointments = PortalAccessLevel.ACT
    messaging = PortalAccessLevel.ACT
    clinical = PortalAccessLevel.ACT
    billing = PortalAccessLevel.ACT
    dob_verified_at = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC))
    granted_by = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")

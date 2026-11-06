import datetime

import factory

from canvas_sdk.v1.data import StaffIdentityVerification


class StaffIdentityVerificationFactory(
    factory.django.DjangoModelFactory[StaffIdentityVerification]
):
    """Factory for creating a StaffIdentityVerification."""

    class Meta:
        model = StaffIdentityVerification

    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    verified_at = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC))
    policy_scope = "http://idmanagement.gov/ns/assurance/ial/2/aal/2"
    name_mismatch = False

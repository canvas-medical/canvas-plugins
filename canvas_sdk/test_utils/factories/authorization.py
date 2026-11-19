import factory

from canvas_sdk.v1.data import Authorization, AuthorizationDiagnosisCode


class AuthorizationFactory(factory.django.DjangoModelFactory[Authorization]):
    """Factory for creating an Authorization."""

    class Meta:
        model = Authorization

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    authorization_number = factory.Sequence(lambda n: f"AUTH-{n:06d}")
    visits_approved = 0
    unlimited_visits = True


class AuthorizationDiagnosisCodeFactory(
    factory.django.DjangoModelFactory[AuthorizationDiagnosisCode]
):
    """Factory for creating an AuthorizationDiagnosisCode."""

    class Meta:
        model = AuthorizationDiagnosisCode

    authorization = factory.SubFactory(AuthorizationFactory)
    code = "E119"
    display = "Type 2 diabetes mellitus without complications"

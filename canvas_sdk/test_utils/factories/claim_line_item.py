import factory

from canvas_sdk.v1.data import ClaimLineItem, ClaimLineItemDiagnosisCode


class ClaimLineItemFactory(factory.django.DjangoModelFactory[ClaimLineItem]):
    """Factory for creating a ClaimLineItem."""

    class Meta:
        model = ClaimLineItem

    from_date = factory.Faker("date", pattern="%Y-%m-%d")
    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")


class ClaimLineItemDiagnosisCodeFactory(
    factory.django.DjangoModelFactory[ClaimLineItemDiagnosisCode]
):
    """Factory for creating a ClaimLineItemDiagnosisCode."""

    class Meta:
        model = ClaimLineItemDiagnosisCode

    line_item = factory.SubFactory(ClaimLineItemFactory)
    code = "T1490"

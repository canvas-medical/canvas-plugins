import factory

from canvas_sdk.v1.data import BannerAlertIntent, ClaimBannerAlert


class ClaimBannerAlertFactory(factory.django.DjangoModelFactory[ClaimBannerAlert]):
    """Factory for creating a ClaimLineItem."""

    class Meta:
        model = ClaimBannerAlert

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    key = "test"
    plugin_name = "test-plugin"
    narrative = "hello"
    intent = BannerAlertIntent.INFO

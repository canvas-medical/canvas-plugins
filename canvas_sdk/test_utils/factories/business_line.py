import factory

from canvas_sdk.v1.data import BusinessLine, BusinessLineSetting
from canvas_sdk.v1.data.business_line import BusinessLineState


class BusinessLineFactory(factory.django.DjangoModelFactory[BusinessLine]):
    """Factory for creating a BusinessLine whose phone number was provisioned."""

    class Meta:
        model = BusinessLine

    name = factory.Sequence(lambda n: f"Business Line {n}")
    description = ""
    area_code = "415"
    subdomain = factory.Sequence(lambda n: f"business-line-{n}")
    active = True
    state = BusinessLineState.STATE_SUCCESS
    organization = factory.SubFactory("canvas_sdk.test_utils.factories.OrganizationFactory")
    logo = ""


class BusinessLineSettingFactory(factory.django.DjangoModelFactory[BusinessLineSetting]):
    """Factory for creating a BusinessLineSetting, by default the reminder message text."""

    class Meta:
        model = BusinessLineSetting

    business_line = factory.SubFactory(BusinessLineFactory)
    name = "appointmentReminderCustomization"
    value = "Please bring your insurance card."

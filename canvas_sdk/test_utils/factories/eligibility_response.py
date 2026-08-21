import factory

from canvas_sdk.v1.data import EligibilityRequest, EligibilityResponse


class EligibilityRequestFactory(factory.django.DjangoModelFactory[EligibilityRequest]):
    """Factory for creating an EligibilityRequest."""

    class Meta:
        model = EligibilityRequest

    coverage = factory.SubFactory("canvas_sdk.test_utils.factories.CoverageFactory")
    trading_partner_id = "test-trading-partner"
    member = factory.LazyFunction(dict)


class EligibilityResponseFactory(factory.django.DjangoModelFactory[EligibilityResponse]):
    """Factory for creating an EligibilityResponse."""

    class Meta:
        model = EligibilityResponse

    coverage = factory.SubFactory("canvas_sdk.test_utils.factories.CoverageFactory")
    deductible = factory.LazyFunction(dict)
    coverage_info = factory.LazyFunction(dict)
    service_type_codes = factory.LazyFunction(list)
    service_types = factory.LazyFunction(list)
    valid_request = True

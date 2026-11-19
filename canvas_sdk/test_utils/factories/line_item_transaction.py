from decimal import Decimal

import factory

from canvas_sdk.v1.data import LineItemAllowed, RemarkCode


class LineItemAllowedFactory(factory.django.DjangoModelFactory[LineItemAllowed]):
    """Factory for creating a LineItemAllowed."""

    class Meta:
        model = LineItemAllowed

    posting = factory.SubFactory("canvas_sdk.test_utils.factories.CoveragePostingFactory")
    billing_line_item = factory.SubFactory("canvas_sdk.test_utils.factories.BillingLineItemFactory")
    claim_line_item = factory.SubFactory(
        "canvas_sdk.test_utils.factories.ClaimLineItemFactory",
        claim=factory.SelfAttribute("..posting.claim"),
    )
    amount = Decimal("80.00")


class RemarkCodeFactory(factory.django.DjangoModelFactory[RemarkCode]):
    """Factory for creating a RemarkCode."""

    class Meta:
        model = RemarkCode

    posting = factory.SubFactory("canvas_sdk.test_utils.factories.CoveragePostingFactory")
    claim_line_item = factory.SubFactory(
        "canvas_sdk.test_utils.factories.ClaimLineItemFactory",
        claim=factory.SelfAttribute("..posting.claim"),
    )
    remark_code = "N130"

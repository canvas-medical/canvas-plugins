from decimal import Decimal

import factory

from canvas_sdk.test_utils.factories._line_item_transaction import LineItemTransactionFactory
from canvas_sdk.v1.data import (
    LineItemAllowed,
    LineItemTransfer,
    NewLineItemAdjustment,
    NewLineItemPayment,
    RemarkCode,
)


class LineItemAllowedFactory(LineItemTransactionFactory):
    """Factory for creating a LineItemAllowed."""

    class Meta:
        model = LineItemAllowed

    amount = Decimal("80.00")


class NewLineItemPaymentFactory(LineItemTransactionFactory):
    """Factory for creating a NewLineItemPayment."""

    class Meta:
        model = NewLineItemPayment

    amount = Decimal("60.00")
    charged = Decimal("100.00")


class NewLineItemAdjustmentFactory(LineItemTransactionFactory):
    """Factory for creating a NewLineItemAdjustment."""

    class Meta:
        model = NewLineItemAdjustment

    amount = Decimal("20.00")
    code = "45"
    group = "CO"
    deviated_from_posting_ruleset = False
    write_off = True


class LineItemTransferFactory(LineItemTransactionFactory):
    """Factory for creating a LineItemTransfer."""

    class Meta:
        model = LineItemTransfer

    amount = Decimal("20.00")
    code = "1"
    group = "PR"
    deviated_from_posting_ruleset = False
    transfer_to_patient = True


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

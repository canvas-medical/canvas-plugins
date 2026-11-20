from typing import Any

import factory

from canvas_sdk.test_utils.factories.billing import BillingLineItemFactory
from canvas_sdk.v1.data import BillingLineItem


def _charge_sharing_the_claim_line_id(transaction: Any) -> BillingLineItem:
    # The views alias billing_line_item_id AS claim_line_item_id, so both ids are the claim line's.
    dbid = transaction.claim_line_item.dbid
    return BillingLineItem.objects.filter(dbid=dbid).first() or BillingLineItemFactory.create(
        dbid=dbid
    )


class LineItemTransactionFactory(factory.django.DjangoModelFactory):
    """Shared declarations for line item transaction factories."""

    class Meta:
        abstract = True

    claim_line_item = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimLineItemFactory")
    posting = factory.SubFactory(
        "canvas_sdk.test_utils.factories.CoveragePostingFactory",
        claim=factory.SelfAttribute("..claim_line_item.claim"),
    )
    billing_line_item = factory.LazyAttribute(_charge_sharing_the_claim_line_id)

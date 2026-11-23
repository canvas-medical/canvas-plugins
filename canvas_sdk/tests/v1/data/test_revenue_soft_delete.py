from decimal import Decimal
from typing import Any

import pytest
from django.db.models import Model

from canvas_sdk.test_utils.factories import (
    BulkPatientPostingFactory,
    CoveragePostingFactory,
    ElectronicRemittanceAdviceFactory,
    LineItemTransferFactory,
    ManualRemittanceAdviceFactory,
    NewLineItemAdjustmentFactory,
    NewLineItemPaymentFactory,
    PatientPostingFactory,
    PaymentCollectionFactory,
)
from canvas_sdk.v1.data import (
    BasePosting,
    BaseRemittanceAdvice,
    BulkPatientPosting,
    Claim,
    CoveragePosting,
    ElectronicRemittanceAdvice,
    LineItemTransfer,
    ManualRemittanceAdvice,
    NewLineItemAdjustment,
    NewLineItemPayment,
    PatientPosting,
    PaymentCollection,
)

_CASES: list[tuple[type[Model], Any]] = [
    (BasePosting, CoveragePostingFactory),
    (CoveragePosting, CoveragePostingFactory),
    (PatientPosting, PatientPostingFactory),
    (BulkPatientPosting, BulkPatientPostingFactory),
    (BaseRemittanceAdvice, ManualRemittanceAdviceFactory),
    (ElectronicRemittanceAdvice, ElectronicRemittanceAdviceFactory),
    (ManualRemittanceAdvice, ManualRemittanceAdviceFactory),
    (NewLineItemPayment, NewLineItemPaymentFactory),
    (NewLineItemAdjustment, NewLineItemAdjustmentFactory),
    (LineItemTransfer, LineItemTransferFactory),
    (PaymentCollection, PaymentCollectionFactory),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("model", "model_factory"), _CASES, ids=lambda c: getattr(c, "__name__", "")
)
def test_soft_deleted_rows_are_hidden(model: type[Model], model_factory: Any) -> None:
    """A row soft-deleted in Canvas is left out of the model's queries."""
    kept = model_factory.create()
    model_factory.create(deleted=True)

    assert [row.pk for row in model._default_manager.all()] == [kept.pk]


@pytest.mark.django_db
def test_claim_postings_skip_soft_deleted_postings() -> None:
    """claim.postings and its active() leave out soft-deleted postings."""
    kept = CoveragePostingFactory.create()
    CoveragePostingFactory.create(
        claim=kept.claim, claim_coverage=kept.claim_coverage, deleted=True
    )

    claim = Claim.objects.get(dbid=kept.claim.dbid)

    assert [p.dbid for p in claim.postings.active()] == [kept.dbid]


@pytest.mark.django_db
def test_paid_amount_skips_soft_deleted_payments() -> None:
    """A posting's paid amount leaves out soft-deleted payments."""
    payment = NewLineItemPaymentFactory.create(amount=Decimal("60.00"))
    NewLineItemPaymentFactory.create(
        posting=payment.posting,
        claim_line_item=payment.claim_line_item,
        amount=Decimal("40.00"),
        deleted=True,
    )

    assert BasePosting.objects.get(dbid=payment.posting.dbid).paid_amount == Decimal("60.00")


@pytest.mark.django_db
def test_payment_collection_postings_skip_soft_deleted_postings() -> None:
    """payment_collection.postings leaves out soft-deleted postings."""
    collection = PaymentCollectionFactory.create()
    kept = CoveragePostingFactory.create(payment_collection=collection)
    CoveragePostingFactory.create(payment_collection=collection, deleted=True)

    assert [p.dbid for p in collection.postings.all()] == [kept.dbid]

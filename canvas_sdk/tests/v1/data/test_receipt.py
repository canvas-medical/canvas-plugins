from datetime import date
from decimal import Decimal

import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, ReceiptFactory
from canvas_sdk.v1.data import PaymentCollection
from canvas_sdk.v1.data.receipt import Receipt


def test_receipt_url_presigns_the_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    """receipt_url returns a presigned URL when the receipt PDF is set."""
    monkeypatch.setattr(
        "canvas_sdk.v1.data.receipt.presigned_url",
        lambda key: f"https://s3.example.com/{key}",
    )

    assert Receipt(receipt="receipts/r.pdf").receipt_url == "https://s3.example.com/receipts/r.pdf"


def test_receipt_url_is_none_when_unset() -> None:
    """receipt_url is None when there is no receipt PDF."""
    assert Receipt(receipt=None).receipt_url is None


def test_amounts_are_zero_without_postings() -> None:
    """The posted/copay amounts are zero when there is nothing to sum."""
    receipt = Receipt(receipt="receipts/r.pdf")

    assert receipt.total_posted_amount == Decimal("0.00")
    assert receipt.copay_amount == Decimal("0.00")


@pytest.mark.django_db
def test_committed_and_reachable_via_payment_collection() -> None:
    """A committed receipt is reachable from its PaymentCollection; amounts are zero with no postings."""
    committer = CanvasUserFactory.create()
    payment_collection = PaymentCollection.objects.create(
        total_collected=Decimal("50.00"),
        method="card",
        check_number="",
        check_date=date(2026, 1, 1),
        deposit_date=date(2026, 1, 1),
        description="",
    )
    receipt = ReceiptFactory.create(payment_collection=payment_collection, committer=committer)
    ReceiptFactory.create(committer=None)  # uncommitted, filtered out by committed()

    assert set(Receipt.objects.committed()) == {receipt}
    assert payment_collection.receipt == receipt
    assert receipt.total_posted_amount == Decimal("0.00")
    assert receipt.copay_amount == Decimal("0.00")

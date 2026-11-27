import pytest
from django.db import IntegrityError, transaction

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    CreditCardChargeFactory,
    PaymentCardFactory,
    PaymentCollectionFactory,
)
from canvas_sdk.v1.data import CreditCardCharge, CreditCardChargeState


@pytest.mark.django_db
def test_credit_card_charge_resolves_from_collection_and_card() -> None:
    """A charge points at its collection and card, and both list the charge."""
    collection = PaymentCollectionFactory.create()
    card = PaymentCardFactory.create()
    charge = CreditCardChargeFactory.create(
        payment_collection=collection,
        payment_method=card,
        state=CreditCardChargeState.SUCCESSFUL,
        provider="custom-processor",
        editors=[3, 7],
    )
    CreditCardChargeFactory.create()

    fetched = CreditCardCharge.objects.get(id=charge.id)

    assert fetched.payment_collection == collection
    assert fetched.payment_method == card
    assert fetched.state == "Successful"
    assert fetched.provider == "custom-processor"
    assert fetched.editors == [3, 7]
    assert fetched.originator is not None
    assert list(collection.credit_card_charges.all()) == [charge]
    assert list(card.credit_card_charges.all()) == [charge]


@pytest.mark.django_db
def test_credit_card_charge_without_payment_method() -> None:
    """A charge made with a single-use card has no stored payment method."""
    charge = CreditCardChargeFactory.create(payment_method=None)

    assert CreditCardCharge.objects.get(id=charge.id).payment_method is None


@pytest.mark.django_db
def test_credit_card_charge_defaults() -> None:
    """A new charge starts pending on Stripe."""
    charge = CreditCardCharge.objects.create(
        originator=CanvasUserFactory.create(),
        payment_collection=PaymentCollectionFactory.create(),
    )

    fetched = CreditCardCharge.objects.get(id=charge.id)

    assert fetched.state == "Pending"
    assert fetched.provider == "stripe"


@pytest.mark.django_db
def test_credit_card_charge_requires_originator() -> None:
    """Every charge has an originator."""
    with pytest.raises(IntegrityError), transaction.atomic():
        CreditCardCharge.objects.create(payment_collection=PaymentCollectionFactory.create())


@pytest.mark.django_db
def test_deleted_credit_card_charges_are_hidden() -> None:
    """Deleted charges are left out of the model and of a collection's charges."""
    collection = PaymentCollectionFactory.create()
    kept = CreditCardChargeFactory.create(payment_collection=collection)
    CreditCardChargeFactory.create(payment_collection=collection, deleted=True)

    assert list(CreditCardCharge.objects.all()) == [kept]
    assert list(collection.credit_card_charges.all()) == [kept]


def test_credit_card_charge_states() -> None:
    """The state field offers the four charge states, by stored value."""
    assert [value for value, _ in CreditCardCharge._meta.get_field("state").flatchoices] == [
        "Pending",
        "Charged",
        "Successful",
        "Failed",
    ]

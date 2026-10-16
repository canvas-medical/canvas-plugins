import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    DmeOrderFactory,
    DmeProductFactory,
    ServiceProviderFactory,
)
from canvas_sdk.v1.data import Command, DmeOrder, DmeProduct, DmeProductCodeSystem


@pytest.mark.django_db
def test_dme_product_is_found_by_code() -> None:
    """A formulary product is found by code, and its id is what OrderDmeCommand takes."""
    wheelchair = DmeProductFactory.create(name="Standard wheelchair", code="K0001")
    DmeProductFactory.create(name="Walker", code="E0130")

    product = DmeProduct.objects.get(code="K0001", code_system=DmeProductCodeSystem.HCPCS)

    assert product.id == wheelchair.id
    assert product.name == "Standard wheelchair"


@pytest.mark.django_db
def test_dme_order_resolves_product_supplier_and_ordering_provider() -> None:
    """An order's foreign keys resolve to the formulary product, supplier and ordering provider."""
    product = DmeProductFactory.create()
    supplier = ServiceProviderFactory.create()
    order = DmeOrderFactory.create(product=product, supplier=supplier)

    fetched = DmeOrder.objects.get(id=order.id)

    assert fetched.product == product
    assert fetched.supplier == supplier
    assert fetched.ordering_provider == order.ordering_provider
    assert list(DmeOrder.objects.filter(product=product)) == [fetched]


@pytest.mark.django_db
def test_dme_order_allows_a_free_text_item() -> None:
    """A free-text item has no formulary product."""
    order = DmeOrderFactory.create(
        product=None, item_name="Custom brace", item_code="", item_code_system=""
    )

    assert DmeOrder.objects.get(id=order.id).product is None


@pytest.mark.django_db
def test_committed_excludes_uncommitted_and_entered_in_error_orders() -> None:
    """committed() returns only signed orders that were not entered in error."""
    user = CanvasUserFactory.create()
    signed = DmeOrderFactory.create(committer=user)
    DmeOrderFactory.create()
    DmeOrderFactory.create(committer=user, entered_in_error=user)

    assert list(DmeOrder.objects.committed()) == [signed]


@pytest.mark.django_db
def test_order_dme_command_anchor_object_is_the_dme_order() -> None:
    """An Order DME command's anchor object resolves to its DmeOrder."""
    order = DmeOrderFactory.create()
    command = Command.objects.create(
        note=order.note,
        patient=order.patient,
        state="committed",
        schema_key="orderDme",
        data={},
        origination_source="plugin",
        anchor_object_type="dmeorder",
        anchor_object_dbid=order.dbid,
    )

    assert command.anchor_object == order

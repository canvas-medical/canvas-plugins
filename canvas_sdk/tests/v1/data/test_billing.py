from decimal import Decimal

import pytest

from canvas_sdk.v1.data import BillingLineItem
from canvas_sdk.value_set.custom import Hcc005v1AnnualWellnessVisit
from canvas_sdk.value_set.value_set import ValueSet


class OfficeVisit(ValueSet):
    """CPT codes, the way eCQM encounter value sets carry them."""

    CPT = {"99213"}


class HospiceEncounter(ValueSet):
    """HCPCS Level II codes, the way eCQM encounter value sets carry them."""

    HCPCSLEVELII = {"G9473"}


def line_items(*codes: str) -> None:
    """One billing line item per code."""
    for code in codes:
        BillingLineItem.objects.create(cpt=code, charge=Decimal("0"), units=1, command_id=1)


def found(value_set: type[ValueSet]) -> set[str]:
    """The codes of the line items `find` returns for a value set."""
    return set(BillingLineItem.objects.find(value_set).values_list("cpt", flat=True))


@pytest.mark.django_db
def test_find_matches_cpt_codes() -> None:
    """A value set's CPT codes match line items billed with them."""
    line_items("99213", "99214")
    assert found(OfficeVisit) == {"99213"}


@pytest.mark.django_db
def test_find_matches_hcpcs_level_ii_codes() -> None:
    """A value set's HCPCS Level II codes match line items billed with them."""
    line_items("G9473", "G0438")
    assert found(HospiceEncounter) == {"G9473"}


@pytest.mark.django_db
def test_find_matches_hcpcs_codes() -> None:
    """Codes under the HCPCS attribute match, as the HCC005 value set relies on."""
    line_items("G0438", "99387", "99213")
    assert found(Hcc005v1AnnualWellnessVisit) == {"G0438", "99387"}

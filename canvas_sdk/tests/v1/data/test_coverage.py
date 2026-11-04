import pytest

from canvas_sdk.test_utils.factories import ClaimCoverageFactory, CoverageFactory
from canvas_sdk.v1.data import ClaimCoverage, Coverage

PLAN_TYPE_LABELS = [
    ("medicare_advantage", "Medicare Advantage"),
    ("CHIP", "CHIP"),
    ("employer", "Employer"),
    ("direct_care", "Direct Care"),
]


@pytest.mark.django_db
@pytest.mark.parametrize(("plan_type", "label"), PLAN_TYPE_LABELS)
def test_coverage_plan_type_display(plan_type: str, label: str) -> None:
    """A coverage's plan type reads back with its display label."""
    coverage = CoverageFactory.create(plan_type=plan_type)

    assert Coverage.objects.get(id=coverage.id).get_plan_type_display() == label


@pytest.mark.django_db
@pytest.mark.parametrize(("plan_type", "label"), PLAN_TYPE_LABELS)
def test_claim_coverage_payer_plan_type_display(plan_type: str, label: str) -> None:
    """A claim coverage's payer plan type reads back with its display label."""
    claim_coverage = ClaimCoverageFactory.create(payer_plan_type=plan_type)

    assert ClaimCoverage.objects.get(id=claim_coverage.id).get_payer_plan_type_display() == label

import pytest


@pytest.mark.django_db
def test_claim_get_coverage_by_payer_id_with_subscriber_number() -> None:
    """
    Checks that the correct coverage is chosen when subscriber_number is provided.
    """
    from canvas_sdk.test_utils.factories.claim import ClaimCoverageFactory, ClaimFactory

    claim = ClaimFactory.create()
    assert claim.get_coverage_by_payer_id("PAYER1", "SUB1") is None

    claim_coverage1 = ClaimCoverageFactory.create(
        payer_id="PAYER1", subscriber_number="SUB1", claim=claim
    )
    claim_coverage2 = ClaimCoverageFactory.create(
        payer_id="PAYER1", subscriber_number="SUB2", claim=claim
    )
    assert claim.get_coverage_by_payer_id("PAYER1", "SUB2") == claim_coverage2
    assert claim.get_coverage_by_payer_id("PAYER1", "SUB1") == claim_coverage1
    # should choose the first when no matching subscriber_number
    assert claim.get_coverage_by_payer_id("PAYER1", "wrong-id") == claim_coverage1


@pytest.mark.django_db
def test_claim_get_coverage_by_payer_id_without_subscriber_number() -> None:
    """
    Checks that the correct coverage is chosen when subscriber_number is not provided.
    """
    from canvas_sdk.test_utils.factories.claim import ClaimCoverageFactory, ClaimFactory

    claim = ClaimFactory.create()
    assert claim.get_coverage_by_payer_id("PAYER1") is None
    assert claim.get_coverage_by_payer_id("PAYER2") is None

    claim_coverage1 = ClaimCoverageFactory.create(payer_id="PAYER1", claim=claim)
    claim_coverage2 = ClaimCoverageFactory.create(payer_id="PAYER2", claim=claim)
    claim_coverage3 = ClaimCoverageFactory.create(payer_id="PAYER2", claim=claim)

    assert claim.get_coverage_by_payer_id("PAYER1") == claim_coverage1
    assert claim.get_coverage_by_payer_id("PAYER2") == claim_coverage2
    assert claim.get_coverage_by_payer_id("PAYER3") is None

    claim_coverage2.active = False
    claim_coverage2.save()
    assert claim.get_coverage_by_payer_id("PAYER2") == claim_coverage3

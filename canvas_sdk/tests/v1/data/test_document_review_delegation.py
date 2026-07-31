"""Tests for the DocumentReviewDelegation model."""

from canvas_sdk.v1.data.document_review_delegation import DocumentReviewDelegation


def test_is_route_back_when_recipient_is_original_owner() -> None:
    """is_route_back is True when the staff recipient is the on_behalf_of owner."""
    delegation = DocumentReviewDelegation()
    delegation.delegated_to_staff_id = 7
    delegation.on_behalf_of_id = 7

    assert delegation.is_route_back is True


def test_is_route_back_false_when_recipient_differs_from_owner() -> None:
    """is_route_back is False when delegated to a staff member other than the owner."""
    delegation = DocumentReviewDelegation()
    delegation.delegated_to_staff_id = 7
    delegation.on_behalf_of_id = 99

    assert delegation.is_route_back is False


def test_is_route_back_false_when_no_staff_recipient() -> None:
    """is_route_back is False for a team delegation with no staff recipient."""
    delegation = DocumentReviewDelegation()
    delegation.delegated_to_staff_id = None
    delegation.on_behalf_of_id = 7

    assert delegation.is_route_back is False

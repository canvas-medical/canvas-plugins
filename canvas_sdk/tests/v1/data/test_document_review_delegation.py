"""Tests for the DocumentReviewDelegation model."""

import pytest

from canvas_sdk.test_utils.factories import DocumentReviewDelegationFactory
from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import (
    ImagingReport,
    LabReport,
    ReferralReport,
    UncategorizedClinicalDocument,
)
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("model", "content_type_model"),
    [
        (LabReport, "labreport"),
        (ImagingReport, "imagingreport"),
        (ReferralReport, "referralreport"),
        (UncategorizedClinicalDocument, "uncategorizedclinicaldocument"),
    ],
)
def test_every_reviewable_document_reads_its_own_delegations(
    model: type[LabReport | ImagingReport | ReferralReport | UncategorizedClinicalDocument],
    content_type_model: str,
) -> None:
    """Each report type reads the delegations linked to its own content type and dbid."""
    document = model(dbid=4321)
    content_type = ContentTypeFactory.create(model=content_type_model)
    sent = DocumentReviewDelegationFactory.create(
        content_type=content_type, object_id=document.dbid, is_active=False
    )
    returned = DocumentReviewDelegationFactory.create(
        content_type=content_type, object_id=document.dbid, is_active=True
    )
    # Same dbid, another document type: not this document's delegation.
    other_type = "labreport" if content_type_model != "labreport" else "imagingreport"
    DocumentReviewDelegationFactory.create(
        content_type=ContentTypeFactory.create(model=other_type), object_id=document.dbid
    )

    assert list(document.delegations) == [sent, returned]
    assert document.active_delegation == returned

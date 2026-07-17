"""Tests for UncategorizedClinicalDocument review-delegation properties."""

import pytest

from canvas_sdk.test_utils.factories import DocumentReviewDelegationFactory
from canvas_sdk.v1.data.uncategorized_clinical_document import UncategorizedClinicalDocument


@pytest.mark.django_db
def test_delegations_returns_only_this_documents_rows() -> None:
    """delegations returns the delegations linked to this document and excludes others."""
    document = UncategorizedClinicalDocument(dbid=4321)
    mine_first = DocumentReviewDelegationFactory.create(object_id=document.dbid, is_active=False)
    mine_second = DocumentReviewDelegationFactory.create(object_id=document.dbid, is_active=True)
    DocumentReviewDelegationFactory.create(object_id=document.dbid + 1)

    assert set(document.delegations) == {mine_first, mine_second}


@pytest.mark.django_db
def test_active_delegation_returns_the_active_row() -> None:
    """active_delegation returns the active delegation for the document."""
    document = UncategorizedClinicalDocument(dbid=4321)
    DocumentReviewDelegationFactory.create(object_id=document.dbid, is_active=False)
    active = DocumentReviewDelegationFactory.create(object_id=document.dbid, is_active=True)

    assert document.active_delegation == active


@pytest.mark.django_db
def test_active_delegation_returns_none_when_none_active() -> None:
    """active_delegation is None when the document has no active delegation."""
    document = UncategorizedClinicalDocument(dbid=4321)
    DocumentReviewDelegationFactory.create(object_id=document.dbid, is_active=False)

    assert document.active_delegation is None

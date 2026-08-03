"""Tests for UncategorizedClinicalDocument review-delegation properties."""

import pytest

from canvas_sdk.test_utils.factories import (
    DocumentCodingFactory,
    DocumentReviewDelegationFactory,
    UncategorizedClinicalDocumentFactory,
)
from canvas_sdk.v1.data.uncategorized_clinical_document import UncategorizedClinicalDocument


@pytest.mark.django_db
def test_delegations_returns_only_this_documents_rows() -> None:
    """Delegations returns the delegations linked to this document and excludes others."""
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


@pytest.mark.django_db
def test_code_coding_round_trips() -> None:
    """The code coding is readable through the data model."""
    coding = DocumentCodingFactory.create(
        system="http://loinc.org", code="34133-9", display="Summary of episode note"
    )
    document = UncategorizedClinicalDocumentFactory.create(code=coding)

    fetched = UncategorizedClinicalDocument.objects.get(dbid=document.dbid)

    assert fetched.code_id == coding.dbid

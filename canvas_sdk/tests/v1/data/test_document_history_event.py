"""Tests for the DocumentHistoryEvent model."""

import datetime
from collections.abc import Callable

import pytest

from canvas_sdk.test_utils.factories import (
    ContentTypeFactory,
    DocumentHistoryEventFactory,
    ImagingReportFactory,
    ImagingReviewFactory,
    LabReportFactory,
    LabReviewFactory,
    ReferralReportFactory,
    ReferralReviewFactory,
    StaffFactory,
    UncategorizedClinicalDocumentFactory,
    UncategorizedClinicalDocumentReviewFactory,
)
from canvas_sdk.v1.data import DocumentHistoryEvent, DocumentHistoryEventType
from canvas_sdk.v1.data.base import Model


@pytest.mark.django_db
def test_history_for_a_document_reads_its_entries_in_order() -> None:
    """A plugin can read one document's timeline by its generic link."""
    first = DocumentHistoryEventFactory.create(object_id=7, comment="Waiting on the agency.")
    reassigned = DocumentHistoryEventFactory.create(
        content_type=first.content_type,
        object_id=7,
        event_type=DocumentHistoryEventType.REASSIGNED,
        recipient_staff=StaffFactory.create(),
    )
    DocumentHistoryEventFactory.create(content_type=first.content_type, object_id=8)

    history = DocumentHistoryEvent.objects.filter(
        content_type__model="uncategorizedclinicaldocument", object_id=7
    ).order_by("created", "dbid")

    assert list(history) == [first, reassigned]


@pytest.mark.django_db
def test_signing_flow_entries_carry_their_recipient_and_signer() -> None:
    """A plugin can follow a form from "sent for signature" to "signed" in its timeline."""
    sender = StaffFactory.create()
    provider = StaffFactory.create()
    sent = DocumentHistoryEventFactory.create(
        object_id=9,
        event_type=DocumentHistoryEventType.SENT_FOR_SIGNATURE,
        actor=sender,
        recipient_staff=provider,
        comment="Please sign.",
    )
    signed = DocumentHistoryEventFactory.create(
        content_type=sent.content_type,
        object_id=9,
        event_type=DocumentHistoryEventType.SIGNED,
        actor=provider,
    )
    signed.signers.add(provider)

    history = DocumentHistoryEvent.objects.filter(
        content_type=sent.content_type, object_id=9
    ).order_by("created", "dbid")

    assert [event.event_type for event in history] == ["sent_for_signature", "signed"]
    assert history[0].recipient_staff == provider
    assert list(history[1].signers.all()) == [provider]


@pytest.mark.django_db
def test_recorded_entry_lists_signers() -> None:
    """A "recorded" entry names whose signatures the document carried."""
    provider = StaffFactory.create()
    recorded = DocumentHistoryEventFactory.create(event_type=DocumentHistoryEventType.RECORDED)
    recorded.signers.add(provider)

    assert list(recorded.signers.all()) == [provider]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("factory", "model_name"),
    [
        (LabReportFactory, "labreport"),
        (ImagingReportFactory, "imagingreport"),
        (ReferralReportFactory, "referralreport"),
        (UncategorizedClinicalDocumentFactory, "uncategorizedclinicaldocument"),
    ],
)
def test_document_resolves_the_reviewable_document(
    factory: Callable[[], Model], model_name: str
) -> None:
    """``document`` returns the report the entry belongs to, of any reviewable type."""
    report = factory()
    event = DocumentHistoryEventFactory.create(
        content_type=ContentTypeFactory.create(model=model_name), object_id=report.dbid
    )

    assert event.document == report


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("factory", "model_name"),
    [
        (LabReviewFactory, "labreview"),
        (ImagingReviewFactory, "imagingreview"),
        (ReferralReviewFactory, "referralreview"),
        (UncategorizedClinicalDocumentReviewFactory, "uncategorizeddocumentreview"),
    ],
)
def test_review_resolves_the_review_command(factory: Callable[[], Model], model_name: str) -> None:
    """``review`` returns the review command a "recorded" entry belongs to."""
    review = factory()
    event = DocumentHistoryEventFactory.create(
        event_type=DocumentHistoryEventType.RECORDED,
        review_content_type=ContentTypeFactory.create(model=model_name),
        review_object_id=review.dbid,
    )

    assert event.review == review


@pytest.mark.django_db
def test_document_and_review_are_none_without_a_supported_link() -> None:
    """An entry with no review link, or a link to an unknown type, resolves to None."""
    event = DocumentHistoryEventFactory.create(
        content_type=ContentTypeFactory.create(model="patient"), object_id=1
    )

    assert event.document is None
    assert event.review is None


def test_comment_hidden_follows_deleted_at() -> None:
    """The comment is hidden once the entry's review was entered in error."""
    event = DocumentHistoryEvent(comment="sent")
    assert event.comment_hidden is False

    event.deleted_at = datetime.datetime(2026, 9, 11, tzinfo=datetime.UTC)
    assert event.comment_hidden is True

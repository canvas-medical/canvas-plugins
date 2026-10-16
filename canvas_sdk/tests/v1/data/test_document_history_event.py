"""Tests for the DocumentHistoryEvent model."""

import datetime

import pytest

from canvas_sdk.test_utils.factories import DocumentHistoryEventFactory, StaffFactory
from canvas_sdk.v1.data import DocumentHistoryEvent, DocumentHistoryEventType


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


def test_comment_hidden_follows_deleted_at() -> None:
    """The comment is hidden once the entry's review was entered in error."""
    event = DocumentHistoryEvent(comment="sent")
    assert event.comment_hidden is False

    event.deleted_at = datetime.datetime(2026, 9, 11, tzinfo=datetime.UTC)
    assert event.comment_hidden is True

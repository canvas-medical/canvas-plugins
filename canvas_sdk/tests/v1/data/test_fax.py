from typing import Any

import pytest
from django.db.models import Model
from factory.django import DjangoModelFactory

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    FaxFactory,
    ImagingOrderActionEventFactory,
    IntegrationTaskActionEventFactory,
    LabOrderActionEventFactory,
    LetterActionEventFactory,
    NoteActionEventFactory,
    ReferralActionEventFactory,
)
from canvas_sdk.v1.data import NoteActionEvent
from canvas_sdk.v1.data.fax import EventTypeChoices

ACTION_EVENTS = [
    pytest.param(
        LetterActionEventFactory,
        "letter",
        "letter_action_events",
        "letteractionevent_set",
        id="letter",
    ),
    pytest.param(NoteActionEventFactory, "note", "action_events", "noteactionevent_set", id="note"),
    pytest.param(
        ReferralActionEventFactory,
        "referral",
        "action_events",
        "referralactionevent_set",
        id="referral",
    ),
    pytest.param(
        ImagingOrderActionEventFactory,
        "imaging_order",
        "action_events",
        "imagingorderactionevent_set",
        id="imaging_order",
    ),
    pytest.param(
        LabOrderActionEventFactory,
        "lab_order",
        "action_events",
        "laborderactionevent_set",
        id="lab_order",
    ),
    pytest.param(
        IntegrationTaskActionEventFactory,
        "integration_task",
        "action_events",
        "integrationtaskactionevent_set",
        id="integration_task",
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("event_factory", "document_field", "document_accessor", "fax_accessor"), ACTION_EVENTS
)
def test_action_event_links_document_sender_and_fax(
    event_factory: type[DjangoModelFactory[Any]],
    document_field: str,
    document_accessor: str,
    fax_accessor: str,
) -> None:
    """Each action event reaches its document, the sending user, and the fax's recipient."""
    sender = CanvasUserFactory.create()
    fax = FaxFactory.create(to_fax_number="+15555550100")
    event = event_factory.create(
        event_type=EventTypeChoices.FAXED,
        delivered_by_fax=False,
        fax_result_msg="Line busy",
        originator=sender,
        fax=fax,
    )
    document: Model = getattr(event, document_field)

    assert getattr(document, document_accessor).get() == event
    assert getattr(fax, fax_accessor).get() == event

    event.refresh_from_db()
    assert event.originator == sender
    assert event.fax is not None
    assert event.fax.to_fax_number == "+15555550100"
    assert event.delivered_by_fax is False
    assert event.fax_result_msg == "Line busy"


@pytest.mark.django_db
def test_failed_faxes_report_sender_and_recipient_number() -> None:
    """A plugin can find failed faxes and report who sent each one and which number failed."""
    sender = CanvasUserFactory.create()
    failed = NoteActionEventFactory.create(
        delivered_by_fax=False,
        originator=sender,
        fax=FaxFactory.create(to_fax_number="+15555550100"),
    )
    NoteActionEventFactory.create(delivered_by_fax=True)
    NoteActionEventFactory.create(delivered_by_fax=None)

    rows = NoteActionEvent.objects.filter(delivered_by_fax=False).values_list(
        "id", "originator", "fax__to_fax_number"
    )

    assert list(rows) == [(failed.id, sender.dbid, "+15555550100")]
